from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from .models import Customer, Order, OrderItem, Product, Service, ServiceRequest


WALK_IN_PHONE = "0000000000"


def get_or_create_walk_in_customer(full_name: str = "", phone: str = "") -> Customer:
    name = (full_name or "").strip() or "Клиент сайта"
    phone_value = "".join(ch for ch in (phone or "") if ch.isdigit()) or WALK_IN_PHONE
    customer, _ = Customer.objects.get_or_create(
        phone=phone_value,
        defaults={"full_name": name, "city": "Москва"},
    )
    if name != "Клиент сайта" and customer.full_name == "Клиент сайта":
        customer.full_name = name
        customer.save(update_fields=["full_name"])
    return customer


def place_demo_order(
    product: Product,
    quantity: int,
    *,
    full_name: str = "",
    phone: str = "",
) -> Order:
    if quantity <= 0:
        raise ValueError("Количество должно быть больше нуля.")
    if not product.is_active:
        raise ValueError("Товар снят с продажи.")
    if product.stock < quantity:
        raise ValueError("Недостаточно товара на складе.")

    with transaction.atomic():
        locked = Product.objects.select_for_update().get(pk=product.pk)
        if locked.stock < quantity:
            raise ValueError("Недостаточно товара на складе.")

        customer = get_or_create_walk_in_customer(full_name, phone)
        order = Order.objects.create(
            customer=customer,
            status=Order.Status.CONFIRMED,
            source=Order.Source.SITE,
            comment=f"Онлайн-заказ с витрины: {locked.name}",
            created_at=timezone.now(),
        )
        OrderItem.objects.create(
            order=order,
            product=locked,
            quantity=quantity,
            unit_price=locked.price,
        )
        locked.stock -= quantity
        locked.save(update_fields=["stock", "updated_at"])
        return order


def create_service_request(
    service: Service,
    *,
    full_name: str,
    phone: str,
    comment: str = "",
) -> ServiceRequest:
    name = (full_name or "").strip()
    phone_digits = "".join(ch for ch in (phone or "") if ch.isdigit())
    if not name or not phone_digits:
        raise ValueError("Укажите имя и телефон.")
    if not service.is_active:
        raise ValueError("Услуга временно недоступна.")

    customer = get_or_create_walk_in_customer(name, phone_digits)
    return ServiceRequest.objects.create(
        customer=customer,
        service=service,
        status=ServiceRequest.Status.NEW,
        comment=comment.strip(),
    )


def format_money(value: Decimal | float | int) -> str:
    number = Decimal(str(value))
    text = f"{number:,.2f}".replace(",", " ")
    return f"{text} ₽"
