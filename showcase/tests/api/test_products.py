from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth.models import User
from ..utils import generate_image_file
from ...models import Category, Product, SiteSettings


class ProductAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(username='admin', password='pass')
        self.user = User.objects.create_user(username='user', password='pass')
        self.category = Category.objects.create(name='Audio', slug='audio')
        image = generate_image_file()
        self.product = Product.objects.create(
            name='AirPods Pro',
            brand='Apple',
            category=self.category,
            price=299.99,
            description='Casque haut de gamme',
            image=image,
            featured=True,
        )

    def test_list_products(self):
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data['results']) >= 1)

    def test_featured_products(self):
        url = reverse('product-featured')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['name'], 'AirPods Pro')

    def test_recent_products(self):
        url = reverse('product-recent')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_stats_endpoint(self):
        url = reverse('product-stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_products', response.data)
