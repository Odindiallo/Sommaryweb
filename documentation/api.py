from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Document, Category, Attachment
from .serializers import (
    DocumentSerializer,
    DocumentListSerializer,
    CategorySerializer,
    AttachmentSerializer
)
from django.db.models import Q

class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user

class IsDocumentAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.document.author == request.user

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    pagination_class = None  # Disable pagination for categories

    @extend_schema(
        description="List all categories",
        responses={200: CategorySerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Create a new category",
        request=CategorySerializer,
        responses={201: CategorySerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_public', 'author', 'tags__name']
    search_fields = ['title', 'content']
    ordering_fields = ['title', 'created_at', 'updated_at', 'views_count']

    def get_serializer_class(self):
        if self.action == 'list':
            return DocumentListSerializer
        return DocumentSerializer

    def get_queryset(self):
        queryset = Document.objects.all()
        if not self.request.user.is_authenticated:
            return queryset.filter(is_public=True)
        elif not self.request.user.is_staff:
            return queryset.filter(Q(is_public=True) | Q(author=self.request.user))
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @extend_schema(
        description="List all documents",
        parameters=[
            OpenApiParameter(name="category", description="Filter by category slug", required=False, type=str),
            OpenApiParameter(name="tags", description="Filter by tag names (comma-separated)", required=False, type=str),
            OpenApiParameter(name="search", description="Search in title and content", required=False, type=str),
            OpenApiParameter(name="ordering", description="Order by field (prefix with - for descending)", required=False, type=str),
        ],
        responses={200: DocumentListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Create a new document",
        request=DocumentSerializer,
        responses={201: DocumentSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        description="Increment the view count of a document",
        responses={200: {"type": "object", "properties": {"views_count": {"type": "integer"}}}}
    )
    @action(detail=True, methods=['post'])
    def increment_views(self, request, slug=None):
        document = self.get_object()
        document.increment_views()
        return Response({'views_count': document.views_count})

class AttachmentViewSet(viewsets.ModelViewSet):
    serializer_class = AttachmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsDocumentAuthorOrReadOnly]
    queryset = Attachment.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['document']
    ordering_fields = ['uploaded_at']
    pagination_class = None  # Disable pagination for attachments

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            return queryset.filter(document__is_public=True)
        elif not self.request.user.is_staff:
            return queryset.filter(
                Q(document__is_public=True) | Q(document__author=self.request.user)
            )
        return queryset

    def perform_create(self, serializer):
        document = serializer.validated_data['document']
        if document.author != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("You can only add attachments to your own documents.")
        serializer.save()

    @extend_schema(
        description="List all attachments",
        parameters=[
            OpenApiParameter(name="document", description="Filter by document ID", required=False, type=int),
            OpenApiParameter(name="ordering", description="Order by field (prefix with - for descending)", required=False, type=str),
        ],
        responses={200: AttachmentSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Create a new attachment",
        request=AttachmentSerializer,
        responses={201: AttachmentSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
