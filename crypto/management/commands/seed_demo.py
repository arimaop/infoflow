from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from crypto.models import Coin, Position, Trade


class Command(BaseCommand):
    help = "Заполняет базу демо-данными (монеты, сделки, позиции)."

    def handle(self, *args, **options):
        btc, _ = Coin.objects.update_or_create(
            symbol="BTC",
            defaults={
                "name": "Bitcoin",
                "tagline": "Цифровое золото и первая криптовалюта",
                "price_usd": Decimal("67420.00"),
                "change_24h_pct": Decimal("2.30"),
                "market_cap_usd": 1_300_000_000_000,
                "volume_24h_usd": 32_000_000_000,
                "dominance_pct": Decimal("51.20"),
            },
        )
        eth, _ = Coin.objects.update_or_create(
            symbol="ETH",
            defaults={
                "name": "Ethereum",
                "tagline": "Базовый слой для DeFi и смарт‑контрактов",
                "price_usd": Decimal("3520.00"),
                "change_24h_pct": Decimal("1.10"),
                "market_cap_usd": 420_000_000_000,
                "volume_24h_usd": 18_000_000_000,
                "dominance_pct": Decimal("17.30"),
            },
        )
        sol, _ = Coin.objects.update_or_create(
            symbol="SOL",
            defaults={
                "name": "Solana",
                "tagline": "Высокопроизводительная сеть для dApp и NFT",
                "price_usd": Decimal("145.00"),
                "change_24h_pct": Decimal("-0.80"),
                "market_cap_usd": 63_000_000_000,
                "volume_24h_usd": 4_200_000_000,
                "dominance_pct": Decimal("3.10"),
            },
        )
        ton, _ = Coin.objects.update_or_create(
            symbol="TON",
            defaults={
                "name": "TON",
                "tagline": "Экосистема Telegram и Web3‑сервисов",
                "price_usd": Decimal("6.20"),
                "change_24h_pct": Decimal("4.50"),
                "market_cap_usd": 21_000_000_000,
                "volume_24h_usd": 1_100_000_000,
                "dominance_pct": Decimal("1.40"),
            },
        )

        Position.objects.update_or_create(
            coin=btc,
            defaults={"quantity": Decimal("0.055"), "avg_price_usd": Decimal("61200.00")},
        )
        Position.objects.update_or_create(
            coin=eth,
            defaults={"quantity": Decimal("1.40"), "avg_price_usd": Decimal("3120.00")},
        )
        Position.objects.update_or_create(
            coin=sol,
            defaults={"quantity": Decimal("32"), "avg_price_usd": Decimal("118.00")},
        )
        Position.objects.update_or_create(
            coin=ton,
            defaults={"quantity": Decimal("850"), "avg_price_usd": Decimal("4.80")},
        )

        now = timezone.now()
        demo_trades = [
            (btc, "BUY", "FILLED", Decimal("66980.00"), Decimal("0.015"), now - timezone.timedelta(hours=3, minutes=12)),
            (eth, "SELL", "FILLED", Decimal("3510.00"), Decimal("0.40"), now - timezone.timedelta(hours=5, minutes=29)),
            (sol, "BUY", "FILLED", Decimal("142.00"), Decimal("8"), now - timezone.timedelta(days=1, hours=1)),
            (ton, "BUY", "CANCELLED", Decimal("6.00"), Decimal("120"), now - timezone.timedelta(days=2, hours=8)),
        ]

        for coin, side, status, price, amount, executed_at in demo_trades:
            Trade.objects.update_or_create(
                coin=coin,
                executed_at=executed_at,
                side=side,
                defaults={
                    "quote_symbol": "USDT",
                    "status": status,
                    "price_usd": price,
                    "amount": amount,
                },
            )

        self.stdout.write(self.style.SUCCESS("Демо-данные добавлены/обновлены."))

