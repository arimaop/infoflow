from django import forms

from .models import Coin, Position, Trade


class CoinForm(forms.ModelForm):
    class Meta:
        model = Coin
        fields = [
            "name",
            "symbol",
            "tagline",
            "price_usd",
            "change_24h_pct",
            "market_cap_usd",
            "volume_24h_usd",
            "dominance_pct",
        ]
        widgets = {
            "tagline": forms.TextInput(attrs={"placeholder": "Короткое описание монеты"}),
        }


class TradeForm(forms.ModelForm):
    class Meta:
        model = Trade
        fields = [
            "executed_at",
            "coin",
            "quote_symbol",
            "side",
            "status",
            "price_usd",
            "amount",
        ]
        widgets = {
            "executed_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = [
            "coin",
            "quantity",
            "avg_price_usd",
        ]

