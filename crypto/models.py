from django.db import models


class Coin(models.Model):
    name = models.CharField(max_length=64)
    symbol = models.CharField(max_length=16, unique=True)

    tagline = models.CharField(max_length=160, blank=True)

    price_usd = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    change_24h_pct = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    market_cap_usd = models.BigIntegerField(default=0)
    volume_24h_usd = models.BigIntegerField(default=0)
    dominance_pct = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-market_cap_usd", "symbol"]

    def __str__(self) -> str:
        return f"{self.symbol} — {self.name}"


class Trade(models.Model):
    class Side(models.TextChoices):
        BUY = "BUY", "BUY"
        SELL = "SELL", "SELL"

    class Status(models.TextChoices):
        FILLED = "FILLED", "Исполнено"
        CANCELLED = "CANCELLED", "Отменено"

    coin = models.ForeignKey(Coin, on_delete=models.PROTECT, related_name="trades")
    quote_symbol = models.CharField(max_length=16, default="USDT")

    side = models.CharField(max_length=8, choices=Side.choices)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.FILLED)

    price_usd = models.DecimalField(max_digits=16, decimal_places=2)
    amount = models.DecimalField(max_digits=18, decimal_places=8)

    executed_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-executed_at", "-id"]

    def __str__(self) -> str:
        return f"{self.side} {self.coin.symbol}/{self.quote_symbol} @ {self.price_usd}"


class Position(models.Model):
    coin = models.ForeignKey(Coin, on_delete=models.PROTECT, related_name="positions")
    quantity = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    avg_price_usd = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    class Meta:
        ordering = ["-quantity", "coin__symbol"]

    def __str__(self) -> str:
        return f"{self.coin.symbol}: {self.quantity}"

    @property
    def value_usd(self):
        return self.quantity * self.coin.price_usd

    @property
    def pnl_usd(self):
        return (self.coin.price_usd - self.avg_price_usd) * self.quantity

    @property
    def pnl_pct(self):
        if self.avg_price_usd == 0:
            return 0
        return (self.coin.price_usd / self.avg_price_usd - 1) * 100
