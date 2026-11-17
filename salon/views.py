from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.db.models import Count, F, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Category, Order, OrderItem, Product, Service, ServiceRequest
from .services import create_service_request, format_money, place_demo_order


def catalog(request):
    products = Product.objects.select_related("category").filter(is_active=True)
    slug = request.GET.get("category", "").strip()
    q = request.GET.get("q", "").strip()
    if slug:
        products = products.filter(category__slug=slug)
    if q:
        products = products.filter(name__icontains=q)

    cards = []
    for product in products:
        cards.append(
            {
                "id": product.id,
                "name": product.name,
                "sku": product.sku,
                "tagline": product.tagline,
                "price": format_money(product.price),
                "stock": product.stock,
                "condition": product.get_condition_display(),
                "condition_code": product.condition,
                "storage": product.storage,
                "color": product.color,
                "category": product.category.name,
                "in_stock": product.stock > 0,
            }
        )

    context = {
        "products": cards,
        "categories": Category.objects.all(),
        "active_category": slug,
        "query": q,
        "stats": {
            "sku": Product.objects.filter(is_active=True).count(),
            "stock": Product.objects.aggregate(total=Sum("stock"))["total"] or 0,
            "orders": Order.objects.exclude(status=Order.Status.CANCELLED).count(),
        },
    }
    return render(request, "salon/catalog.html", context)


@require_POST
def buy_product(request, product_id: int):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    raw_qty = request.POST.get("quantity", "1").strip()
    try:
        quantity = int(raw_qty)
        order = place_demo_order(
            product,
            quantity,
            full_name=request.POST.get("full_name", ""),
            phone=request.POST.get("phone", ""),
        )
    except (ValueError, InvalidOperation) as exc:
        messages.error(request, str(exc) if str(exc) else "Укажите корректное количество.")
        return redirect("salon:catalog")

    messages.success(
        request,
        f"Заказ {order.number}: {quantity} × {product.name} "
        f"на {format_money(product.price * quantity)}. Остаток обновлён.",
    )
    return redirect("salon:orders")


def orders(request):
    rows = []
    qs = Order.objects.select_related("customer").prefetch_related("items__product")
    for index, order in enumerate(qs, start=1):
        items = ", ".join(
            f"{item.product.name} × {item.quantity}" for item in order.items.all()
        )
        rows.append(
            {
                "num": index,
                "number": order.number,
                "time": timezone.localtime(order.created_at).strftime("%d.%m %H:%M"),
                "customer": order.customer.full_name,
                "items": items or "—",
                "total": format_money(order.total),
                "status": order.get_status_display(),
                "status_code": order.status,
                "source": order.get_source_display(),
            }
        )
    return render(request, "salon/orders.html", {"orders": rows})


def warehouse(request):
    cards = []
    stock_sum = Decimal("0")
    retail_sum = Decimal("0")
    for product in Product.objects.select_related("category"):
        stock_sum += product.stock_value
        retail_sum += product.retail_value
        cards.append(
            {
                "name": product.name,
                "sku": product.sku,
                "category": product.category.name,
                "stock": product.stock,
                "price": format_money(product.price),
                "purchase": format_money(product.purchase_price),
                "margin": format_money(product.margin),
                "stock_value": format_money(product.stock_value),
                "low": product.stock <= 2,
            }
        )
    summary = {
        "positions": Product.objects.count(),
        "units": Product.objects.aggregate(total=Sum("stock"))["total"] or 0,
        "stock_sum": format_money(stock_sum),
        "retail_sum": format_money(retail_sum),
    }
    return render(request, "salon/warehouse.html", {"products": cards, "summary": summary})


def analytics(request):
    since = timezone.now() - timezone.timedelta(days=30)
    active_orders = Order.objects.exclude(status=Order.Status.CANCELLED)
    orders_30d = active_orders.filter(created_at__gte=since)
    revenue = OrderItem.objects.filter(order__in=active_orders).aggregate(
        total=Sum(F("unit_price") * F("quantity"))
    )["total"] or Decimal("0")
    revenue_30d = OrderItem.objects.filter(order__in=orders_30d).aggregate(
        total=Sum(F("unit_price") * F("quantity"))
    )["total"] or Decimal("0")
    count_30d = orders_30d.count()
    avg_check = (revenue_30d / count_30d) if count_30d else Decimal("0")

    kpis = [
        {"label": "Заказов за 30 дней", "value": str(count_30d), "hint": "без отменённых"},
        {"label": "Выручка за 30 дней", "value": format_money(revenue_30d), "hint": "сумма позиций"},
        {"label": "Средний чек", "value": format_money(avg_check), "hint": "выручка / заказы"},
        {"label": "Выручка всего", "value": format_money(revenue), "hint": "все подтверждённые продажи"},
    ]

    category_rows = (
        OrderItem.objects.filter(order__in=active_orders)
        .values("product__category__name")
        .annotate(qty=Sum("quantity"), amount=Sum(F("unit_price") * F("quantity")))
        .order_by("-amount")
    )
    total_amount = sum((row["amount"] or Decimal("0") for row in category_rows), Decimal("0"))
    allocations = []
    for row in category_rows:
        amount = row["amount"] or Decimal("0")
        pct = int(round((amount / total_amount) * 100)) if total_amount else 0
        allocations.append(
            {
                "name": row["product__category__name"] or "Прочее",
                "pct": pct,
            }
        )

    status_counts = (
        Order.objects.values("status").annotate(total=Count("id")).order_by("status")
    )
    status_map = dict(Order.Status.choices)
    notes = [
        "Покупка с витрины уменьшает остаток и сразу попадает в заказы и KPI.",
        "Заявки на услуги (trade-in, настройка, диагностика) ведутся отдельно от продаж.",
        "Закупка и розница задаются в карточке товара — маржа видна на складе.",
    ]
    return render(
        request,
        "salon/analytics.html",
        {
            "kpis": kpis,
            "allocations": allocations,
            "notes": notes,
            "status_counts": [
                {"label": status_map.get(row["status"], row["status"]), "total": row["total"]}
                for row in status_counts
            ],
        },
    )


def services_page(request):
    services = Service.objects.filter(is_active=True)
    return render(request, "salon/services.html", {"services": services})


@require_POST
def request_service(request, service_id: int):
    service = get_object_or_404(Service, pk=service_id, is_active=True)
    try:
        create_service_request(
            service,
            full_name=request.POST.get("full_name", ""),
            phone=request.POST.get("phone", ""),
            comment=request.POST.get("comment", ""),
        )
    except ValueError as exc:
        messages.error(request, str(exc))
        return redirect("salon:services")

    messages.success(
        request,
        f"Заявка на «{service.name}» принята. Менеджер салона свяжется с вами.",
    )
    return redirect("salon:services")


def about(request):
    return render(request, "salon/about.html")
