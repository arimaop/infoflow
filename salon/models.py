from decimal import Decimal

from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField("Название", max_length=80)
    slug = models.SlugField("Код", max_length=80, unique=True)
    sort_order = models.PositiveSmallIntegerField("Порядок", default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    class Condition(models.TextChoices):
        NEW = "NEW", "Новое"
        REFURBISHED = "REFURBISHED", "Восстановленное"
        USED = "USED", "Б/у"

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Категория",
    )
    name = models.CharField("Название", max_length=160)
    sku = models.CharField("Артикул", max_length=32, unique=True)
    tagline = models.CharField("Краткое описание", max_length=200, blank=True)
    description = models.TextField("Описание", blank=True)

    storage = models.CharField("Память", max_length=32, blank=True)
    color = models.CharField("Цвет", max_length=48, blank=True)
    year = models.PositiveSmallIntegerField("Год модели", null=True, blank=True)
    condition = models.CharField(
        "Состояние",
        max_length=16,
        choices=Condition.choices,
        default=Condition.NEW,
    )

    price = models.DecimalField("Цена, ₽", max_digits=12, decimal_places=2, default=0)
    purchase_price = models.DecimalField(
        "Закупка, ₽",
        max_digits=12,
        decimal_places=2,
        default=0,
    )
    stock = models.PositiveIntegerField("Остаток", default=0)
    is_featured = models.BooleanField("В подборке", default=False)
    is_active = models.BooleanField("В продаже", default=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        ordering = ["category__sort_order", "name"]
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self) -> str:
        return f"{self.name} ({self.sku})"

    @property
    def margin(self) -> Decimal:
        return self.price - self.purchase_price

    @property
    def stock_value(self) -> Decimal:
        return self.purchase_price * self.stock

    @property
    def retail_value(self) -> Decimal:
        return self.price * self.stock


class Customer(models.Model):
    full_name = models.CharField("ФИО", max_length=160)
    phone = models.CharField("Телефон", max_length=32)
    email = models.EmailField("Email", blank=True)
    city = models.CharField("Город", max_length=80, blank=True, default="Москва")
    notes = models.TextField("Заметки", blank=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        ordering = ["full_name"]
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self) -> str:
        return f"{self.full_name} · {self.phone}"


class Employee(models.Model):
    full_name = models.CharField("ФИО", max_length=160)
    role = models.CharField("Должность", max_length=80)
    phone = models.CharField("Телефон", max_length=32, blank=True)
    is_active = models.BooleanField("Работает", default=True)

    class Meta:
        ordering = ["full_name"]
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self) -> str:
        return f"{self.full_name} — {self.role}"


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = "NEW", "Новый"
        CONFIRMED = "CONFIRMED", "Подтверждён"
        ISSUED = "ISSUED", "Выдан"
        CANCELLED = "CANCELLED", "Отменён"

    class Source(models.TextChoices):
        SITE = "SITE", "Сайт"
        SALON = "SALON", "Салон"

    number = models.CharField("Номер", max_length=20, blank=True, unique=True)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="Клиент",
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        related_name="orders",
        verbose_name="Менеджер",
        null=True,
        blank=True,
    )
    status = models.CharField(
        "Статус",
        max_length=16,
        choices=Status.choices,
        default=Status.NEW,
    )
    source = models.CharField(
        "Источник",
        max_length=16,
        choices=Source.choices,
        default=Source.SITE,
    )
    comment = models.CharField("Комментарий", max_length=240, blank=True)
    created_at = models.DateTimeField("Создан", default=timezone.now)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self) -> str:
        return self.number or f"Заказ #{self.pk}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.number:
            self.number = f"BL-{self.pk:05d}"
            super().save(update_fields=["number"])

    @property
    def total(self) -> Decimal:
        return sum((item.line_total for item in self.items.all()), Decimal("0"))


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Заказ",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name="Товар",
    )
    quantity = models.PositiveIntegerField("Количество", default=1)
    unit_price = models.DecimalField("Цена на момент продажи, ₽", max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказов"

    def __str__(self) -> str:
        return f"{self.product.name} × {self.quantity}"

    @property
    def line_total(self) -> Decimal:
        return self.unit_price * self.quantity


class Service(models.Model):
    name = models.CharField("Услуга", max_length=160)
    price = models.DecimalField("Цена, ₽", max_digits=10, decimal_places=2, default=0)
    duration_min = models.PositiveIntegerField("Длительность, мин", default=30)
    description = models.TextField("Описание", blank=True)
    is_active = models.BooleanField("Доступна", default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def __str__(self) -> str:
        return self.name


class ServiceRequest(models.Model):
    class Status(models.TextChoices):
        NEW = "NEW", "Новая"
        SCHEDULED = "SCHEDULED", "Записана"
        DONE = "DONE", "Выполнена"
        CANCELLED = "CANCELLED", "Отменена"

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="service_requests",
        verbose_name="Клиент",
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name="requests",
        verbose_name="Услуга",
    )
    status = models.CharField(
        "Статус",
        max_length=16,
        choices=Status.choices,
        default=Status.NEW,
    )
    scheduled_at = models.DateTimeField("На когда", null=True, blank=True)
    comment = models.CharField("Комментарий", max_length=240, blank=True)
    created_at = models.DateTimeField("Создана", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Заявка на услугу"
        verbose_name_plural = "Заявки на услуги"

    def __str__(self) -> str:
        return f"{self.service.name} — {self.customer.full_name}"
