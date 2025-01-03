from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from ..models import Category, Document, Attachment

User = get_user_model()

class CategoryModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            description='Test Description'
        )

    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Test Category')
        self.assertEqual(self.category.description, 'Test Description')
        self.assertEqual(self.category.slug, 'test-category')

    def test_category_str(self):
        self.assertEqual(str(self.category), 'Test Category')

class DocumentModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Test Category',
            description='Test Description'
        )
        self.document = Document.objects.create(
            title='Test Document',
            content='Test Content',
            category=self.category,
            author=self.user,
            is_public=True
        )

    def test_document_creation(self):
        self.assertEqual(self.document.title, 'Test Document')
        self.assertEqual(self.document.content, 'Test Content')
        self.assertEqual(self.document.category, self.category)
        self.assertEqual(self.document.author, self.user)
        self.assertTrue(self.document.is_public)
        self.assertEqual(self.document.views_count, 0)
        self.assertEqual(self.document.slug, slugify(self.document.title))

    def test_document_str(self):
        self.assertEqual(str(self.document), 'Test Document')

    def test_get_absolute_url(self):
        expected_url = f'/docs/{self.document.slug}/'
        self.assertEqual(self.document.get_absolute_url(), expected_url)

    def test_increment_views(self):
        initial_views = self.document.views_count
        self.document.increment_views()
        self.assertEqual(self.document.views_count, initial_views + 1)

    def test_document_hierarchy(self):
        child_doc = Document.objects.create(
            title='Child Document',
            content='Child Content',
            category=self.category,
            author=self.user,
            parent=self.document
        )
        
        hierarchy = self.document.get_hierarchy()
        self.assertIsNone(hierarchy['parent'])
        self.assertIn(child_doc, hierarchy['children'])

class AttachmentModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Test Category'
        )
        self.document = Document.objects.create(
            title='Test Document',
            content='Test Content',
            category=self.category,
            author=self.user
        )

    def test_attachment_str(self):
        attachment = Attachment.objects.create(
            document=self.document,
            name='test.txt'
        )
        self.assertEqual(str(attachment), 'test.txt')

    def test_file_extension(self):
        attachment = Attachment.objects.create(
            document=self.document,
            name='test.pdf',
            file='test.pdf'
        )
        self.assertEqual(attachment.file_extension, '.pdf')

    def test_is_image(self):
        image_attachment = Attachment.objects.create(
            document=self.document,
            name='test.jpg',
            file='test.jpg',
            content_type='image/jpeg'
        )
        pdf_attachment = Attachment.objects.create(
            document=self.document,
            name='test.pdf',
            file='test.pdf',
            content_type='application/pdf'
        )
        
        self.assertTrue(image_attachment.is_image)
        self.assertFalse(pdf_attachment.is_image)

    def test_is_pdf(self):
        pdf_attachment = Attachment.objects.create(
            document=self.document,
            name='test.pdf',
            file='test.pdf',
            content_type='application/pdf'
        )
        self.assertTrue(pdf_attachment.is_pdf)
