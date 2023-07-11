"""
Tests for the ingredients API.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    """Create and return an ingredient detail url."""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(email='user@example.com', password='passw123'):
    """Create and return a user"""
    return get_user_model().objects.create_user(
        email=email, password=password)


class PublicIngredientsApiTests(TestCase):
    """Test for authenticated users."""

    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_requests(self):
        res = self.client.get(path=INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test for the authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving a list of ingredients"""
        Ingredient.objects.create(user=self.user, name="Spinach")
        Ingredient.objects.create(user=self.user, name="Bread")

        res = self.client.get(INGREDIENTS_URL)

        tags = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test if the ingredients are limited to a user"""
        user1 = create_user(email="user1@example.com")
        ingredient1 = Ingredient.objects.create(user=user1, name="Spinach") # noqa
        ingredient2 = Ingredient.objects.create(user=self.user, name="Tomato")

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient2.name)
        self.assertEqual(res.data[0]['id'], ingredient2.id)

    def test_update_ingredients(self):
        """Test updating ingredient."""
        ingredient = Ingredient.objects.create(user=self.user, name='Spinach')

        payload = {'name': 'Tomato'}
        url = detail_url(ingredient.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(payload['name'], ingredient.name)

    def test_delete_ingredient(self):
        """Test deleting ingredient."""

        ingredient = Ingredient.objects.create(user=self.user, name='Onion')

        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())
