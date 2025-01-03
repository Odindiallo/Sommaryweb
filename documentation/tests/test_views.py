from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from ..models import Document, Category, Attachment
from taggit.models import Tag

User = get_user_model()

class DocumentViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
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

    def test_document_list_view(self):
        # Anonymous users should see public documents
        response = self.client.get(reverse('documentation:document_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'documentation/document_list.html')
        self.assertContains(response, 'Test Document')

        # Authenticated users should see their own private documents
        self.client.login(username='testuser', password='testpass123')
        private_doc = Document.objects.create(
            title='Private Document',
            content='Private Content',
            category=self.category,
            author=self.user,
            is_public=False
        )
        response = self.client.get(reverse('documentation:document_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Private Document')

    def test_document_create_view(self):
        # Anonymous users should be redirected to login
        response = self.client.get(reverse('documentation:document_create'))
        self.assertRedirects(
            response,
            f'/users/login/?next={reverse("documentation:document_create")}'
        )

        # Authenticated users should be able to create documents
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('documentation:document_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'documentation/document_form.html')

        # Test creating a new document
        post_data = {
            'title': 'New Document',
            'content': 'New Content',
            'category': self.category.id,
            'is_public': True,
            'tags': 'test, new',
            'parent': '',
            'order': 0,
            'is_index': False
        }
        response = self.client.post(reverse('documentation:document_create'), post_data, follow=True)
        self.assertRedirects(response, reverse('documentation:document_list'))
        self.assertTrue(Document.objects.filter(title='New Document').exists())

    def test_document_update_view(self):
        # Anonymous users should be redirected to login
        response = self.client.get(reverse('documentation:document_update', kwargs={'slug': self.document.slug}))
        self.assertRedirects(
            response,
            f'/users/login/?next={reverse("documentation:document_update", kwargs={"slug": self.document.slug})}'
        )

        # Authenticated users should be able to update their own documents
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('documentation:document_update', kwargs={'slug': self.document.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'documentation/document_form.html')

        # Test updating the document
        post_data = {
            'title': 'Updated Document',
            'content': 'Updated Content',
            'category': self.category.id,
            'is_public': True,
            'tags': 'updated',
            'parent': '',
            'order': 0,
            'is_index': False
        }
        response = self.client.post(reverse('documentation:document_update', kwargs={'slug': self.document.slug}), post_data, follow=True)
        self.assertRedirects(response, reverse('documentation:document_list'))
        self.document.refresh_from_db()
        self.assertEqual(self.document.title, 'Updated Document')
        self.assertEqual(self.document.content, 'Updated Content')

    def test_document_delete_view(self):
        # Anonymous users should be redirected to login
        response = self.client.get(reverse('documentation:document_delete', kwargs={'slug': self.document.slug}))
        self.assertRedirects(
            response,
            f'/users/login/?next={reverse("documentation:document_delete", kwargs={"slug": self.document.slug})}'
        )

        # Authenticated users should be able to delete their own documents
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('documentation:document_delete', kwargs={'slug': self.document.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'documentation/document_confirm_delete.html')

        # Test deleting the document
        response = self.client.post(reverse('documentation:document_delete', kwargs={'slug': self.document.slug}), follow=True)
        self.assertRedirects(response, reverse('documentation:document_list'))
        self.assertFalse(Document.objects.filter(id=self.document.id).exists())

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

        # Test that logged-in user can't update other's document
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('documentation:document_update', kwargs={'slug': other_doc.slug}))
        self.assertEqual(response.status_code, 404)  # Document not found in user's queryset

        # Test that logged-in user can't delete other's document
        response = self.client.get(reverse('documentation:document_delete', kwargs={'slug': other_doc.slug}))
        self.assertEqual(response.status_code, 404)  # Document not found in user's queryset
