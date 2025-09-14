# core/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Article, Publisher


class ArticleAPITestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = APIClient()
        self.client.login(username='testuser', password='password')

        self.publisher = Publisher.objects.create(name="Test Publisher")
        self.publisher.subscribers.add(self.user)

        self.article1 = Article.objects.create(
            title="Subscribed Article",
            content="Content for subscribers",
            publisher=self.publisher,
            approved=True
        )
        self.article2 = Article.objects.create(
            title="Other Article",
            content="Content not for subscriber",
            approved=True
        )

    def test_get_articles_for_subscriber(self):
        """Test that API returns only articles from publishers the user is subscribed to."""
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

      
        returned_titles = [article['title'] for article in response.json()]
        self.assertIn(self.article1.title, returned_titles)
        self.assertNotIn(self.article2.title, returned_titles)

    def test_create_article(self):
        """Test that authenticated user can create an article."""
        data = {
            "title": "New Article",
            "content": "This is a test article",
            "publisher": self.publisher.id,
            "approved": False
        }
        response = self.client.post('/api/articles/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Article.objects.count(), 3)
        self.assertEqual(Article.objects.get(title="New Article").content, "This is a test article")
