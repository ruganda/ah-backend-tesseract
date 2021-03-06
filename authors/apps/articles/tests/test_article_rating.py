from django.shortcuts import get_object_or_404
from rest_framework import status

from authors.apps.articles.models import Article
from . import BaseTest


class ArticleTests(BaseTest):

    def test_valid_rating(self):
        self.assertEqual(self.rate_article.status_code, status.HTTP_201_CREATED)

    def test_invalid_ratings(self):
        self.client.post("/api/article/create", self.article_data, format="json")
        response = self.client.post('/api/article/rating/', self.test_invalid_ratings, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_article_rating(self):
        response = self.client.post('/api/article/rating/', self.test_invalid_article_ratings, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_double_rating(self):
        self.assertEqual(self.rate_article_again.status_code, status.HTTP_400_BAD_REQUEST)

    def test_average_rating(self):
        article_instance = get_object_or_404(Article, title=self.article_update_data["title"])
        self.assertEqual(article_instance.average_rating, 3)

    def test_user_rating_is_in_article(self):
        self.assertIn('users_rating', self.get_article_after_rating.data)
        self.assertEqual(self.get_article_after_rating.data["users_rating"], 3)
