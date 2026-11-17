from decimal import Decimal, InvalidOperation

from django import forms

from .models import OrderItem, Product, Service


class PlainDecimalWidget(forms.TextInput):
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


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            "price": _decimal_widget(),
            "purchase_price": _decimal_widget(),
        }


class OrderItemInlineForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = "__all__"
        widgets = {
            "unit_price": _decimal_widget(),
        }


class ServiceAdminForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = "__all__"
        widgets = {
            "price": _decimal_widget(),
        }
