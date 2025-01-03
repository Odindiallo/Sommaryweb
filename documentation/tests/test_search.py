from django.test import TestCase
from unittest import skipUnless
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.postgres.search import SearchVector
from django.db import connection
from ..models import Document, Category
from taggit.models import Tag

User = get_user_model()

@skipUnless(connection.vendor == 'postgresql', 'Full-text search requires PostgreSQL.')
class DocumentSearchTests(TestCase):
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
        self.doc1 = Document.objects.create(
            title='Python Programming Guide',
            content='Learn Python programming from scratch',
            category=self.category,
            author=self.user,
            is_public=True
        )
        self.doc1.tags.add('python', 'programming', 'guide')

        self.doc2 = Document.objects.create(
            title='Django Web Development',
            content='Build web applications with Django',
            category=self.category,
            author=self.user,
            is_public=True
        )
        self.doc2.tags.add('python', 'django', 'web')

        self.doc3 = Document.objects.create(
            title='JavaScript Basics',
            content='Introduction to JavaScript',
            category=self.category,
            author=self.user,
            is_public=True
        )
        self.doc3.tags.add('javascript', 'web')

        # Update search vectors
        Document.objects.update(
            search_vector=(
                SearchVector('title', weight='A') +
                SearchVector('content', weight='B')
            )
        )

    def test_basic_search(self):
        url = reverse('documentation:document_list')
        response = self.client.get(url, {'q': 'python'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python Programming Guide')
        self.assertContains(response, 'Django Web Development')
        self.assertNotContains(response, 'JavaScript Basics')

    def test_tag_search(self):
        url = reverse('documentation:document_list')
        response = self.client.get(url, {'tag': ['web']})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django Web Development')
        self.assertContains(response, 'JavaScript Basics')
        self.assertNotContains(response, 'Python Programming Guide')

    def test_category_filter(self):
        new_category = Category.objects.create(
            name='New Category',
            description='New Description'
        )
        doc4 = Document.objects.create(
            title='Test Document',
            content='Test Content',
            category=new_category,
            author=self.user,
            is_public=True
        )

        url = reverse('documentation:document_list')
        response = self.client.get(url, {'category': self.category.slug})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python Programming Guide')
        self.assertNotContains(response, 'Test Document')

    def test_combined_search(self):
        url = reverse('documentation:document_list')
        response = self.client.get(url, {
            'q': 'web',
            'tag': ['python'],
            'sort': 'relevance'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django Web Development')
        self.assertNotContains(response, 'JavaScript Basics')

    def test_private_document_search(self):
        private_doc = Document.objects.create(
            title='Private Document',
            content='This is private',
            category=self.category,
            author=self.user,
            is_public=False
        )
        private_doc.tags.add('private')

        # Update search vector for the new document
        Document.objects.filter(pk=private_doc.pk).update(
            search_vector=(
                SearchVector('title', weight='A') +
                SearchVector('content', weight='B')
            )
        )

        # Test anonymous user can't see private documents
        url = reverse('documentation:document_list')
        response = self.client.get(url, {'q': 'private'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Private Document')

        # Test author can see their private documents
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(url, {'q': 'private'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Private Document')

    def test_sort_options(self):
        # Test sort by title
        url = reverse('documentation:document_list')
        response = self.client.get(url, {'sort': 'title'})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        django_pos = content.find('Django Web Development')
        javascript_pos = content.find('JavaScript Basics')
        python_pos = content.find('Python Programming Guide')
        self.assertTrue(django_pos < javascript_pos < python_pos)

        # Test sort by views
        self.doc1.increment_views()  # 1 view
        self.doc2.increment_views()  # 1 view
        self.doc2.increment_views()  # 2 views
        response = self.client.get(url, {'sort': 'views'})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertTrue(content.find('Django Web Development') < content.find('Python Programming Guide'))

class BasicDocumentTests(TestCase):
    """Tests that don't require PostgreSQL"""
    
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
        self.doc = Document.objects.create(
            title='Test Document',
            content='Test Content',
            category=self.category,
            author=self.user,
            is_public=True
        )

    def test_document_creation(self):
        self.assertEqual(self.doc.title, 'Test Document')
        self.assertEqual(self.doc.content, 'Test Content')
        self.assertEqual(self.doc.author, self.user)
        self.assertEqual(self.doc.category, self.category)
        self.assertTrue(self.doc.is_public)

    def test_document_str(self):
        self.assertEqual(str(self.doc), 'Test Document')

    def test_document_slug(self):
        self.assertEqual(self.doc.slug, 'test-document')

    def test_document_views(self):
        initial_views = self.doc.views
        self.doc.increment_views()
        self.doc.refresh_from_db()
        self.assertEqual(self.doc.views, initial_views + 1)
