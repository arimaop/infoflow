from django.contrib import admin

from .models import Coin, Position, Trade


@admin.register(Coin)
class CoinAdmin(admin.ModelAdmin):
    list_display = ("symbol", "name", "price_usd", "change_24h_pct", "market_cap_usd", "updated_at")
    search_fields = ("symbol", "name")
    list_filter = ("updated_at",)


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ("executed_at", "coin", "side", "status", "price_usd", "amount", "quote_symbol")
    list_filter = ("side", "status", "coin")
    search_fields = ("coin__symbol", "coin__name")
    date_hierarchy = "executed_at"


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("coin", "quantity", "avg_price_usd")
    search_fields = ("coin__symbol", "coin__name")
