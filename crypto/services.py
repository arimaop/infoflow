from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from .models import Coin, Position, Trade


def apply_demo_buy(coin: Coin, amount: Decimal) -> Position:
    """Условная покупка: сделка в историю + обновление позиции в портфеле."""
    if amount <= 0:
        raise ValueError("Количество должно быть больше нуля.")

    with transaction.atomic():
        Trade.objects.create(
            coin=coin,
            quote_symbol="USDT",
            side=Trade.Side.BUY,
            status=Trade.Status.FILLED,
            price_usd=coin.price_usd,
            amount=amount,
            executed_at=timezone.now(),
        )

        position = Position.objects.select_for_update().filter(coin=coin).order_by("pk").first()
        if position is None:
            position = Position.objects.create(
                coin=coin,
                quantity=amount,
                avg_price_usd=coin.price_usd,
            )
            return position

        old_qty = position.quantity
        old_avg = position.avg_price_usd
        new_qty = old_qty + amount
        position.quantity = new_qty
        if new_qty > 0:
            position.avg_price_usd = ((old_qty * old_avg) + (amount * coin.price_usd)) / new_qty
        position.save(update_fields=["quantity", "avg_price_usd"])
        return position
