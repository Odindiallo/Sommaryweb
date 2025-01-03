from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from ..models import Category, Document, Attachment

User = get_user_model()

class DocumentAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
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
        self.client.force_authenticate(user=self.user)

    def test_list_documents(self):
        url = reverse('documentation:document-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Document')

    def test_create_document(self):
        url = reverse('documentation:document-list')
        data = {
            'title': 'New API Document',
            'content': 'API Content',
            'category_id': self.category.id,
            'is_public': True,
            'tags': ['api', 'test']
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Document.objects.count(), 2)
        self.assertEqual(Document.objects.get(title='New API Document').author, self.user)

    def test_retrieve_document(self):
        url = reverse('documentation:document-detail', kwargs={'slug': self.document.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Document')

    def test_update_document(self):
        url = reverse('documentation:document-detail', kwargs={'slug': self.document.slug})
        data = {
            'title': 'Updated API Document',
            'content': 'Updated API Content',
            'category_id': self.category.id,
            'is_public': True,
            'tags': ['updated']
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.document.refresh_from_db()
        self.assertEqual(self.document.title, 'Updated API Document')

    def test_delete_document(self):
        url = reverse('documentation:document-detail', kwargs={'slug': self.document.slug})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Document.objects.count(), 0)

    def test_unauthorized_access(self):
        # Create document as another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        other_doc = Document.objects.create(
            title='Other Document',
            content='Other Content',
            category=self.category,
            author=other_user,
            is_public=False
        )

        # Test that user can't update other's document
        url = reverse('documentation:document-detail', kwargs={'slug': other_doc.slug})
        data = {
            'title': 'Unauthorized Update',
            'content': other_doc.content,
            'category_id': self.category.id,
            'is_public': True
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test that user can't delete other's document
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class CategoryAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Test Category',
            description='Test Description'
        )
        self.client.force_authenticate(user=self.user)

    def test_list_categories(self):
        url = reverse('documentation:category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Category')

    def test_create_category(self):
        url = reverse('documentation:category-list')
        data = {
            'name': 'New Category',
            'description': 'New Description'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)

class AttachmentAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Test Category')
        self.document = Document.objects.create(
            title='Test Document',
            content='Test Content',
            category=self.category,
            author=self.user
        )
        self.attachment = Attachment.objects.create(
            document=self.document,
            name='test.txt',
            file='test.txt',
            content_type='text/plain'
        )
        self.client.force_authenticate(user=self.user)

    def test_list_attachments(self):
        url = reverse('documentation:attachment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'test.txt')
