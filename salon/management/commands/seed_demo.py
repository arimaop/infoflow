from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from salon.models import (
    Category,
    Customer,
    Employee,
    Order,
    OrderItem,
    Product,
    Service,
    ServiceRequest,
)


class Command(BaseCommand):
    help = "Заполняет базу демо-данными салона связи BlueLine."

    def handle(self, *args, **options):
        categories = {}
        for order, (name, slug) in enumerate(
            [
                ("iPhone", "iphone"),
                ("Mac", "mac"),
                ("iPad", "ipad"),
                ("Watch", "watch"),
                ("Аудио", "audio"),
                ("Аксессуары", "accessories"),
            ],
            start=1,
        ):
            categories[slug], _ = Category.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "sort_order": order},
            )

        products = [
            {
                "sku": "IP16P-256-NT",
                "category": "iphone",
                "name": "iPhone 16 Pro 256 GB",
                "tagline": "Титан Natural, камера 5×, USB-C",
                "storage": "256 GB",
                "color": "Natural Titanium",
                "year": 2024,
                "condition": Product.Condition.NEW,
                "price": Decimal("124990"),
                "purchase_price": Decimal("108500"),
                "stock": 4,
                "is_featured": True,
            },
            {
                "sku": "IP16-128-BK",
                "category": "iphone",
                "name": "iPhone 16 128 GB",
                "tagline": "Базовый флагман для повседневных задач",
                "storage": "128 GB",
                "color": "Black",
                "year": 2024,
                "condition": Product.Condition.NEW,
                "price": Decimal("79990"),
                "purchase_price": Decimal("70500"),
                "stock": 7,
                "is_featured": True,
            },
            {
                "sku": "IP15-128-BL-R",
                "category": "iphone",
                "name": "iPhone 15 128 GB",
                "tagline": "Восстановленный, проверка батареи 92%+",
                "storage": "128 GB",
                "color": "Blue",
                "year": 2023,
                "condition": Product.Condition.REFURBISHED,
                "price": Decimal("59990"),
                "purchase_price": Decimal("47200"),
                "stock": 5,
                "is_featured": True,
            },
            {
                "sku": "MBA13-M3-256",
                "category": "mac",
                "name": "MacBook Air 13\" M3",
                "tagline": "Тонкий ноутбук для учёбы и работы",
                "storage": "256 GB",
                "color": "Midnight",
                "year": 2024,
                "condition": Product.Condition.NEW,
                "price": Decimal("119990"),
                "purchase_price": Decimal("104000"),
                "stock": 3,
                "is_featured": True,
            },
            {
                "sku": "MBP14-M3-512",
                "category": "mac",
                "name": "MacBook Pro 14\" M3",
                "tagline": "Для монтажа, кода и тяжёлых задач",
                "storage": "512 GB",
                "color": "Space Black",
                "year": 2024,
                "condition": Product.Condition.NEW,
                "price": Decimal("189990"),
                "purchase_price": Decimal("168000"),
                "stock": 2,
            },
            {
                "sku": "IPAD-AIR-M2",
                "category": "ipad",
                "name": "iPad Air 11\" M2",
                "tagline": "Планшет с поддержкой Apple Pencil Pro",
                "storage": "128 GB",
                "color": "Blue",
                "year": 2024,
                "condition": Product.Condition.NEW,
                "price": Decimal("74990"),
                "purchase_price": Decimal("65200"),
                "stock": 4,
            },
            {
                "sku": "WATCH-S10-46",
                "category": "watch",
                "name": "Apple Watch Series 10 46 мм",
                "tagline": "Тонкий корпус, Always-On дисплей",
                "storage": "GPS",
                "color": "Silver",
                "year": 2024,
                "condition": Product.Condition.NEW,
                "price": Decimal("44990"),
                "purchase_price": Decimal("38100"),
                "stock": 6,
            },
            {
                "sku": "APP2-USB-C",
                "category": "audio",
                "name": "AirPods Pro 2 USB-C",
                "tagline": "Шумоподавление и Adaptive Audio",
                "storage": "",
                "color": "White",
                "year": 2023,
                "condition": Product.Condition.NEW,
                "price": Decimal("22990"),
                "purchase_price": Decimal("17800"),
                "stock": 12,
            },
            {
                "sku": "MAGSAFE-CH",
                "category": "accessories",
                "name": "Зарядка MagSafe",
                "tagline": "Оригинальный аксессуар для iPhone",
                "storage": "",
                "color": "White",
                "year": 2024,
                "condition": Product.Condition.NEW,
                "price": Decimal("4990"),
                "purchase_price": Decimal("3200"),
                "stock": 18,
            },
            {
                "sku": "USBC-CABLE",
                "category": "accessories",
                "name": "Кабель USB-C 1 м",
                "tagline": "Плетёный кабель для быстрой зарядки",
                "storage": "",
                "color": "White",
                "year": 2024,
                "condition": Product.Condition.NEW,
                "price": Decimal("2490"),
                "purchase_price": Decimal("1100"),
                "stock": 30,
            },
        ]

        product_map = {}
        for item in products:
            slug = item.pop("category")
            obj, _ = Product.objects.update_or_create(
                sku=item["sku"],
                defaults={**item, "category": categories[slug], "is_active": True},
            )
            product_map[obj.sku] = obj
            item["category"] = slug

        anna, _ = Employee.objects.update_or_create(
            full_name="Анна Крылова",
            defaults={"role": "Старший консультант", "phone": "+7 495 120-16-00", "is_active": True},
        )
        Employee.objects.update_or_create(
            full_name="Илья Орлов",
            defaults={"role": "Сервис-инженер", "phone": "+7 495 120-16-01", "is_active": True},
        )

        walk_in, _ = Customer.objects.update_or_create(
            phone="0000000000",
            defaults={"full_name": "Клиент сайта", "city": "Москва"},
        )
        marina, _ = Customer.objects.update_or_create(
            phone="79031234567",
            defaults={
                "full_name": "Марина Соколова",
                "email": "marina@example.com",
                "city": "Москва",
            },
        )
        dmitry, _ = Customer.objects.update_or_create(
            phone="79035551212",
            defaults={
                "full_name": "Дмитрий Волков",
                "email": "dmitry@example.com",
                "city": "Химки",
            },
        )

        now = timezone.now()
        order_specs = [
            (walk_in, Order.Status.ISSUED, Order.Source.SITE, now - timezone.timedelta(days=12), "APP2-USB-C", 1),
            (marina, Order.Status.ISSUED, Order.Source.SALON, now - timezone.timedelta(days=5), "IP15-128-BL-R", 1),
            (dmitry, Order.Status.CONFIRMED, Order.Source.SITE, now - timezone.timedelta(days=1), "IP16-128-BK", 1),
            (marina, Order.Status.CANCELLED, Order.Source.SITE, now - timezone.timedelta(days=8), "USBC-CABLE", 2),
        ]

        for customer, status, source, created_at, sku, qty in order_specs:
            product = product_map[sku]
            order, _ = Order.objects.update_or_create(
                customer=customer,
                created_at=created_at,
                defaults={
                    "status": status,
                    "source": source,
                    "employee": anna,
                    "comment": "Демо-заказ",
                },
            )
            OrderItem.objects.update_or_create(
                order=order,
                product=product,
                defaults={"quantity": qty, "unit_price": product.price},
            )

        services = [
            ("Диагностика устройства", Decimal("0"), 20, "Проверка батареи, дисплея и модулей связи."),
            ("Настройка с нуля", Decimal("1490"), 40, "Apple ID, перенос данных, eSIM, базовые приложения."),
            ("Trade-in оценка", Decimal("0"), 25, "Оценка вашего iPhone/Mac в зачёт новой покупки."),
            ("Замена стекла", Decimal("8900"), 90, "Замена защитного стекла / дисплейного модуля по модели."),
            ("Подбор тарифа и eSIM", Decimal("500"), 15, "Активация eSIM и консультация по тарифам операторов."),
        ]
        service_map = {}
        for name, price, duration, description in services:
            obj, _ = Service.objects.update_or_create(
                name=name,
                defaults={
                    "price": price,
                    "duration_min": duration,
                    "description": description,
                    "is_active": True,
                },
            )
            service_map[name] = obj

        ServiceRequest.objects.update_or_create(
            customer=marina,
            service=service_map["Trade-in оценка"],
            defaults={
                "status": ServiceRequest.Status.SCHEDULED,
                "scheduled_at": now + timezone.timedelta(days=1, hours=3),
                "comment": "iPhone 13, батарея 86%",
            },
        )

        self.stdout.write(self.style.SUCCESS("Демо-данные салона BlueLine добавлены/обновлены."))
