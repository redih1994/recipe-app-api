"""
Tests for models
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models

class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new user"""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'samplepass')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test if the user has entered the email address"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'samplepass')

    def test_create_superuser(self):
        """Test the creation of the superuser"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'samplepass'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test creating a recipe successfully"""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='Simple Recipe',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Sample description'
        )

        self.assertEqual(str(recipe), recipe.title)
