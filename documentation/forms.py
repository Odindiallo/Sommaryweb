from django import forms
from .models import Document, Attachment, Category
from ckeditor.widgets import CKEditorWidget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class DocumentForm(forms.ModelForm):
    attachments = MultipleFileField(
        required=False,
        help_text='You can upload multiple files at once.'
    )
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'tag-input',
            'placeholder': 'Add tags (comma separated)'
        })
    )

    class Meta:
        model = Document
        fields = ['title', 'content', 'category', 'is_public', 'parent', 'order', 'is_index']
        widgets = {
            'content': CKEditorWidget(),
            'parent': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.NumberInput(attrs={'class': 'form-input', 'min': '0'}),
            'is_index': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('title', css_class='form-group col-md-8'),
                Column('category', css_class='form-group col-md-4'),
                css_class='form-row'
            ),
            'content',
            Row(
                Column('tags', css_class='form-group col-md-6'),
                Column('parent', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('order', css_class='form-group col-md-4'),
                Column('is_public', css_class='form-group col-md-4'),
                Column('is_index', css_class='form-group col-md-4'),
                css_class='form-row'
            ),
            'attachments',
            Submit('submit', 'Save Document', css_class='btn btn-primary')
        )

        # Add help texts
        self.fields['title'].help_text = "The title of your document"
        self.fields['content'].help_text = "The main content of your document"
        self.fields['category'].help_text = "The category this document belongs to"
        self.fields['tags'].help_text = "Add tags to help organize and find your document"
        self.fields['parent'].help_text = "Select a parent document if this is a sub-document"
        self.fields['is_public'].help_text = "Make this document visible to everyone"
        self.fields['order'].help_text = "Order in which this document appears (lower numbers appear first)"
        self.fields['is_index'].help_text = "Check if this is the main page of a section"

        # Set initial values
        self.fields['parent'].queryset = Document.objects.all().order_by('title')
        self.fields['parent'].required = False
        self.fields['parent'].empty_label = "No parent (top-level document)"
        self.fields['order'].initial = 0
        self.fields['is_index'].initial = False

        if self.instance.pk:
            self.fields['tags'].initial = ', '.join(tag.name for tag in self.instance.tags.all())

    def clean_tags(self):
        tags = self.cleaned_data.get('tags', '')
        if isinstance(tags, list):
            return tags
        if not tags:
            return []
        return [tag.strip() for tag in tags.split(',') if tag.strip()]

    def save(self, commit=True):
        document = super().save(commit=False)
        if commit:
            document.save()
            # Handle tags
            document.tags.set(self.clean_tags())
            # Handle attachments
            attachments = self.cleaned_data.get('attachments')
            if attachments:
                for file in attachments:
                    Attachment.objects.create(
                        document=document,
                        file=file,
                        name=file.name,
                        content_type=file.content_type
                    )
        return document

class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ['file', 'name']
