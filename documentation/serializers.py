from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Document, Category, Attachment
from taggit.serializers import TagListSerializerField, TaggitSerializer
from django.utils.text import slugify

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Generate slug from name if not provided
        if 'slug' not in validated_data:
            validated_data['slug'] = slugify(validated_data['name'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Update slug if name changes
        if 'name' in validated_data and validated_data['name'] != instance.name:
            validated_data['slug'] = slugify(validated_data['name'])
        return super().update(instance, validated_data)

class AttachmentSerializer(serializers.ModelSerializer):
    file_size_display = serializers.CharField(source='human_readable_size', read_only=True)
    
    class Meta:
        model = Attachment
        fields = ['id', 'file', 'name', 'uploaded_at', 'file_size', 'file_size_display', 'content_type']
        read_only_fields = ['id', 'uploaded_at', 'file_size', 'file_size_display', 'content_type']

class DocumentSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source='category',
        queryset=Category.objects.all(),
        write_only=True
    )
    attachments = AttachmentSerializer(many=True, read_only=True)
    parent = serializers.PrimaryKeyRelatedField(queryset=Document.objects.all(), allow_null=True, required=False)
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'slug', 'content', 'category', 'category_id', 'author',
            'created_at', 'updated_at', 'is_public', 'views_count',
            'tags', 'parent', 'children', 'order', 'is_index',
            'attachments'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'views_count']

    def get_children(self, obj):
        children = obj.children.all()
        return DocumentListSerializer(children, many=True).data

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['author'] = request.user
        return super().create(validated_data)

class DocumentListSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source='category',
        queryset=Category.objects.all(),
        write_only=True
    )

    class Meta:
        model = Document
        fields = [
            'id', 'title', 'slug', 'category', 'category_id', 'author',
            'created_at', 'updated_at', 'is_public', 'views_count',
            'tags', 'order', 'is_index'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'views_count']
