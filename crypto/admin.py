from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .admin_forms import CoinAdminForm, PositionAdminForm, TradeAdminForm
from .models import Coin, Position, Trade


class AdminRowNumberMixin:
    """Сквозная нумерация 1, 2, 3… в списке (не зависит от пропусков ID в БД)."""

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
            '<a class="btn btn-xs btn-warning" href="{}" title="Редактировать запись">'
            '<i class="fas fa-edit"></i> Изменить</a>',
            url,
        )


class CoinRelatedAdminMixin:
    coin_field_name = "coin"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == self.coin_field_name:
            kwargs["queryset"] = Coin.objects.order_by("symbol")
            kwargs["empty_label"] = "Выберите монету"

            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda coin: f"{coin.symbol} — {coin.name}"
            return formfield
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Coin)
class CoinAdmin(AdminRowNumberMixin, AdminEditLinkMixin, admin.ModelAdmin):
    form = CoinAdminForm
    save_on_top = True
    list_display = (
        "row_number",
        "symbol",
        "name",
        "price_usd",
        "change_24h_display",
        "market_cap_usd",
        "volume_24h_usd",
        "dominance_pct",
        "updated_at",
        "edit_link",
    )
    list_display_links = ("row_number", "symbol", "name")
    list_filter = ("updated_at",)
    search_fields = ("symbol", "name", "tagline")
    ordering = ("-market_cap_usd", "symbol")
    readonly_fields = ("updated_at",)
    fieldsets = (
        (None, {"fields": ("name", "symbol", "tagline")}),
        (
            "Рыночные данные",
            {
                "fields": (
                    "price_usd",
                    "change_24h_pct",
                    "market_cap_usd",
                    "volume_24h_usd",
                    "dominance_pct",
                )
            },
        ),
        ("Служебное", {"fields": ("updated_at",)}),
    )

    @admin.display(description="24ч, %", ordering="change_24h_pct")
    def change_24h_display(self, obj):
        color = "#2e9661" if obj.change_24h_pct >= 0 else "#d36161"
        return format_html(
            '<span style="color:{}; font-weight:600;">{}%</span>',
            color,
            f"{obj.change_24h_pct:+.2f}",
        )


@admin.register(Trade)
class TradeAdmin(AdminRowNumberMixin, AdminEditLinkMixin, CoinRelatedAdminMixin, admin.ModelAdmin):
    form = TradeAdminForm
    save_on_top = True
    list_display = (
        "row_number",
        "executed_at",
        "coin_display",
        "side_display",
        "status",
        "price_usd",
        "amount",
        "quote_symbol",
        "edit_link",
    )
    list_display_links = ("row_number", "executed_at")
    list_filter = ("side", "status", "coin", "executed_at")
    search_fields = ("coin__symbol", "coin__name", "quote_symbol")
    date_hierarchy = "executed_at"
    ordering = ("-executed_at", "-pk")
    readonly_fields = ("created_at",)
    fieldsets = (
        (None, {"fields": ("coin", "quote_symbol", "executed_at")}),
        ("Параметры сделки", {"fields": ("side", "status", "price_usd", "amount")}),
        ("Служебное", {"fields": ("created_at",)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("coin")

    @admin.display(description="Монета", ordering="coin__symbol")
    def coin_display(self, obj):
        return f"{obj.coin.symbol} — {obj.coin.name}"

    @admin.display(description="Сторона", ordering="side")
    def side_display(self, obj):
        if obj.side == Trade.Side.BUY:
            return format_html('<span style="color:#2e9661; font-weight:600;">BUY</span>')
        return format_html('<span style="color:#d36161; font-weight:600;">SELL</span>')


@admin.register(Position)
class PositionAdmin(AdminRowNumberMixin, AdminEditLinkMixin, CoinRelatedAdminMixin, admin.ModelAdmin):
    form = PositionAdminForm
    save_on_top = True
    list_display = (
        "row_number",
        "coin_display",
        "quantity",
        "avg_price_usd",
        "value_usd_display",
        "pnl_usd_display",
        "pnl_pct_display",
        "edit_link",
    )
    list_display_links = ("row_number",)
    search_fields = ("coin__symbol", "coin__name")
    ordering = ("coin__symbol",)
    computed_readonly_fields = ("value_usd_display", "pnl_usd_display", "pnl_pct_display")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("coin")

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return ()
        return self.computed_readonly_fields

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (None, {"fields": ("coin", "quantity", "avg_price_usd")}),
        ]
        if obj and obj.pk:
            fieldsets.append(
                (
                    "Расчётные показатели",
                    {"fields": self.computed_readonly_fields},
                )
            )
        return fieldsets

    @admin.display(description="Монета", ordering="coin__symbol")
    def coin_display(self, obj):
        return f"{obj.coin.symbol} — {obj.coin.name}"

    @admin.display(description="Стоимость, $")
    def value_usd_display(self, obj):
        if not obj or not obj.coin_id:
            return "—"
        return f"{obj.value_usd:,.2f}"

    @admin.display(description="PnL, $")
    def pnl_usd_display(self, obj):
        if not obj or not obj.coin_id:
            return "—"
        pnl = obj.pnl_usd
        color = "#2e9661" if pnl >= 0 else "#d36161"
        return format_html(
            '<span style="color:{}; font-weight:600;">{}</span>',
            color,
            f"{pnl:+,.2f}",
        )

    @admin.display(description="PnL, %")
    def pnl_pct_display(self, obj):
        if not obj or not obj.coin_id:
            return "—"
        pnl = obj.pnl_pct
        color = "#2e9661" if pnl >= 0 else "#d36161"
        return format_html(
            '<span style="color:{}; font-weight:600;">{}%</span>',
            color,
            f"{pnl:+.2f}",
        )
