from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .admin_forms import OrderItemInlineForm, ProductAdminForm, ServiceAdminForm
from .models import (
    Category,
    Customer,
    Employee,
    Order,
    OrderItem,
    Product,
    Service,
    ServiceRequest,
)


class AdminRowNumberMixin:
    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        if hasattr(response, "context_data") and response.context_data:
            changelist = response.context_data.get("cl")
            if changelist is not None:
                start = (changelist.page_num - 1) * changelist.list_per_page + 1
                for offset, obj in enumerate(changelist.result_list):
                    obj._admin_row_number = start + offset
        return response

    @admin.display(description="№", ordering="pk")
    def row_number(self, obj):
        return getattr(obj, "_admin_row_number", "—")


class AdminEditLinkMixin:
    @admin.display(description="Изменить")
    def edit_link(self, obj):
        opts = obj._meta
        url = reverse(
            f"admin:{opts.app_label}_{opts.model_name}_change",
            args=[obj.pk],
        )
        return format_html(
            '<a class="btn btn-xs btn-primary" href="{}" title="Редактировать запись">'
            '<i class="fas fa-edit"></i> Изменить</a>',
            url,
        )


@admin.register(Category)
class CategoryAdmin(AdminRowNumberMixin, AdminEditLinkMixin, admin.ModelAdmin):
    list_display = ("row_number", "name", "slug", "sort_order", "edit_link")
    list_display_links = ("row_number", "name")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    form = OrderItemInlineForm
    extra = 1
    autocomplete_fields = ("product",)


@admin.register(Product)
class ProductAdmin(AdminRowNumberMixin, AdminEditLinkMixin, admin.ModelAdmin):
    form = ProductAdminForm
    save_on_top = True
    list_display = (
        "row_number",
        "name",
        "sku",
        "category",
        "condition",
        "price",
        "stock",
        "is_active",
        "edit_link",
    )
    list_display_links = ("row_number", "name")
    list_filter = ("category", "condition", "is_active", "is_featured")
    search_fields = ("name", "sku", "tagline", "color")
    readonly_fields = ("updated_at",)
    autocomplete_fields = ("category",)
    fieldsets = (
        (None, {"fields": ("category", "name", "sku", "tagline", "description")}),
        ("Характеристики", {"fields": ("storage", "color", "year", "condition")}),
        ("Цены и склад", {"fields": ("purchase_price", "price", "stock")}),
        ("Витрина", {"fields": ("is_featured", "is_active", "updated_at")}),
    )


@admin.register(Customer)
class CustomerAdmin(AdminRowNumberMixin, AdminEditLinkMixin, admin.ModelAdmin):
    list_display = ("row_number", "full_name", "phone", "email", "city", "edit_link")
    list_display_links = ("row_number", "full_name")
    search_fields = ("full_name", "phone", "email")


@admin.register(Employee)
class EmployeeAdmin(AdminRowNumberMixin, AdminEditLinkMixin, admin.ModelAdmin):
    list_display = ("row_number", "full_name", "role", "phone", "is_active", "edit_link")
    list_display_links = ("row_number", "full_name")
    list_filter = ("is_active", "role")
    search_fields = ("full_name", "role")


@admin.register(Order)
class OrderAdmin(AdminRowNumberMixin, AdminEditLinkMixin, admin.ModelAdmin):
    save_on_top = True
    inlines = [OrderItemInline]
    list_display = (
        "row_number",
        "number",
        "created_at",
        "customer",
        "status",
        "source",
        "total_display",
        "edit_link",
    )
    list_display_links = ("row_number", "number")
    list_filter = ("status", "source", "created_at")
    search_fields = ("number", "customer__full_name", "customer__phone")
    date_hierarchy = "created_at"
    autocomplete_fields = ("customer", "employee")
    readonly_fields = ("number",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("customer").prefetch_related("items")

    @admin.display(description="Сумма, ₽")
    def total_display(self, obj):
        return f"{obj.total:,.2f}"


@admin.register(Service)
class ServiceAdmin(AdminRowNumberMixin, AdminEditLinkMixin, admin.ModelAdmin):
    form = ServiceAdminForm
    list_display = ("row_number", "name", "price", "duration_min", "is_active", "edit_link")
    list_display_links = ("row_number", "name")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(ServiceRequest)
class ServiceRequestAdmin(AdminRowNumberMixin, AdminEditLinkMixin, admin.ModelAdmin):
    list_display = (
        "row_number",
        "created_at",
        "service",
        "customer",
        "status",
        "scheduled_at",
        "edit_link",
    )
    list_display_links = ("row_number", "created_at")
    list_filter = ("status", "service", "created_at")
    search_fields = ("customer__full_name", "customer__phone", "service__name")
    autocomplete_fields = ("customer", "service")
