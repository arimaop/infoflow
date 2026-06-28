from decimal import Decimal, InvalidOperation

from django import forms

from .models import Coin, Position, Trade


class PlainDecimalWidget(forms.TextInput):
    """Текстовое поле вместо number — без 1e-8 и прочей научной нотации."""

    input_type = "text"

    def format_value(self, value):
        if value in (None, ""):
            return ""
        try:
            number = Decimal(str(value))
        except InvalidOperation:
            return str(value)
        text = format(number, "f")
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        return text or "0"


def _decimal_widget(**attrs):
    defaults = {
        "class": "vTextField",
        "inputmode": "decimal",
        "autocomplete": "off",
    }
    defaults.update(attrs)
    return PlainDecimalWidget(attrs=defaults)


class CoinAdminForm(forms.ModelForm):
    class Meta:
        model = Coin
        fields = "__all__"
        widgets = {
            "price_usd": _decimal_widget(),
            "change_24h_pct": _decimal_widget(),
            "dominance_pct": _decimal_widget(),
        }


class TradeAdminForm(forms.ModelForm):
    class Meta:
        model = Trade
        fields = "__all__"
        widgets = {
            "price_usd": _decimal_widget(),
            "amount": _decimal_widget(),
        }


class PositionAdminForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = "__all__"
        widgets = {
            "quantity": _decimal_widget(),
            "avg_price_usd": _decimal_widget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["coin"].queryset = Coin.objects.order_by("symbol")
        self.fields["coin"].empty_label = "Выберите монету"
        self.fields["coin"].label_from_instance = lambda coin: f"{coin.symbol} — {coin.name}"
