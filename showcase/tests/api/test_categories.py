from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth.models import User
from ...models import Category, Product
from ..utils import generate_image_file


class CategoryAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(username='admin', password='pass')
        self.user = User.objects.create_user(username='user', password='pass')
        self.parent = Category.objects.create(name='Électronique', slug='electronique')
        self.child = Category.objects.create(name='Audio', slug='audio', parent=self.parent)
        image = generate_image_file()
        self.product = Product.objects.create(
            name='AirPods Pro',
            brand='Apple',
            category=self.child,
            price=299.99,
            description='Casque haut de gamme',
            image=image,
        )

    def test_main_categories(self):
        url = reverse('category-main-categories')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_category_products(self):
        url = reverse('category-products', args=[self.child.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
