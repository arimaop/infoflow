from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from salon.models import Category, Customer, Order, Product, Service
from salon.services import place_demo_order


class SalonSiteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="iPhone", slug="iphone", sort_order=1)
        cls.product = Product.objects.create(
            category=cls.category,
            name="iPhone 16 128 GB",
            sku="IP16-128",
            price=Decimal("79990.00"),
            purchase_price=Decimal("70000.00"),
            stock=5,
            is_active=True,
        )
        cls.service = Service.objects.create(
            name="Настройка с нуля",
            price=Decimal("1490.00"),
            duration_min=40,
            is_active=True,
        )

    def test_catalog_renders_products(self):
        response = self.client.get(reverse("salon:catalog"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "iPhone 16 128 GB")
        self.assertContains(response, "BlueLine")

    def test_buy_creates_order_and_decreases_stock(self):
        response = self.client.post(
            reverse("salon:buy_product", args=[self.product.pk]),
            {"quantity": "2", "full_name": "Тест Клиент", "phone": "79001112233"},
        )
        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.items.first().quantity, 2)

    def test_buy_rejects_overstock(self):
        response = self.client.post(
            reverse("salon:buy_product", args=[self.product.pk]),
            {"quantity": "9"},
        )
        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)
        self.assertEqual(Order.objects.count(), 0)

    def test_service_request(self):
        response = self.client.post(
            reverse("salon:request_service", args=[self.service.pk]),
            {"full_name": "Анна", "phone": "79005554433", "comment": "Нужна eSIM"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.service.requests.count(), 1)

    def test_about_page(self):
        response = self.client.get(reverse("salon:about"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ИП")


class AdminPanelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Mac", slug="mac")
        cls.product = Product.objects.create(
            category=cls.category,
            name="MacBook Air 13",
            sku="MBA13",
            price=Decimal("119990"),
            stock=3,
        )

    def setUp(self):
        user_model = get_user_model()
        self.admin_user = user_model.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="test-pass-123",
        )
        self.client = Client()
        self.client.force_login(self.admin_user)

    def test_product_changelist(self):
        response = self.client.get(reverse("admin:salon_product_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "MacBook Air 13")

    def test_admin_index_has_clear_button(self):
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Очистить")

    def test_place_demo_order_helper(self):
        order = place_demo_order(self.product, 1)
        self.assertTrue(order.number.startswith("BL-"))
        self.assertEqual(Customer.objects.filter(phone="0000000000").count(), 1)
