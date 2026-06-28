from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from crypto.models import Coin, Position, Trade


class AdminPanelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.coin = Coin.objects.create(
            symbol="BTC",
            name="Bitcoin",
            tagline="Test coin",
            price_usd=Decimal("50000.00"),
            change_24h_pct=Decimal("1.25"),
            market_cap_usd=1_000_000,
            volume_24h_usd=100_000,
            dominance_pct=Decimal("50.00"),
        )
        cls.eth = Coin.objects.create(
            symbol="ETH",
            name="Ethereum",
            price_usd=Decimal("3000.00"),
        )

    def setUp(self):
        user_model = get_user_model()
        self.admin_user = user_model.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="test-pass-123",
        )
        self.client = Client()
        self.client.force_login(self.admin_user)

    def test_coin_changelist_and_add(self):
        response = self.client.get(reverse("admin:crypto_coin_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bitcoin")

        response = self.client.get(reverse("admin:crypto_coin_add"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="name"')

    def test_trade_changelist_add_and_save(self):
        response = self.client.get(reverse("admin:crypto_trade_changelist"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("admin:crypto_trade_add"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bitcoin")
        self.assertContains(response, 'name="coin"')
        self.assertNotContains(response, 'type="number"')

        response = self.client.post(
            reverse("admin:crypto_trade_add"),
            {
                "coin": self.coin.pk,
                "quote_symbol": "USDT",
                "executed_at_0": timezone.localtime().date().isoformat(),
                "executed_at_1": "12:00:00",
                "side": Trade.Side.BUY,
                "status": Trade.Status.FILLED,
                "price_usd": "49500.50",
                "amount": "0.125",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Trade.objects.filter(
                coin=self.coin,
                amount=Decimal("0.125"),
                price_usd=Decimal("49500.50"),
            ).exists()
        )

    def test_position_changelist_add_and_save(self):
        position = Position.objects.create(
            coin=self.coin,
            quantity=Decimal("0.5"),
            avg_price_usd=Decimal("42000.00"),
        )

        response = self.client.get(reverse("admin:crypto_position_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "BTC")

        response = self.client.get(reverse("admin:crypto_position_change", args=[position.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Расчётные показатели")

        response = self.client.get(reverse("admin:crypto_position_add"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bitcoin")
        self.assertContains(response, 'name="coin"')
        self.assertContains(response, 'name="quantity"')
        self.assertNotContains(response, "Расчётные показатели")
        self.assertNotContains(response, 'type="number"')

        response = self.client.post(
            reverse("admin:crypto_position_add"),
            {
                "coin": self.eth.pk,
                "quantity": "1.25",
                "avg_price_usd": "2800.00",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Position.objects.filter(
                coin=self.eth,
                quantity=Decimal("1.25"),
                avg_price_usd=Decimal("2800.00"),
            ).exists()
        )

    def test_position_change_computed_fields(self):
        position = Position.objects.create(
            coin=self.coin,
            quantity=Decimal("1"),
            avg_price_usd=Decimal("40000.00"),
        )
        response = self.client.get(reverse("admin:crypto_position_change", args=[position.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "50")

    def test_coin_edit_via_change_form(self):
        url = reverse("admin:crypto_coin_change", args=[self.coin.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="name"')
        self.assertContains(response, "Сохранить")

        response = self.client.post(
            url,
            {
                "name": "Bitcoin Updated",
                "symbol": "BTC",
                "tagline": self.coin.tagline,
                "price_usd": "51000.00",
                "change_24h_pct": "2.00",
                "market_cap_usd": self.coin.market_cap_usd,
                "volume_24h_usd": self.coin.volume_24h_usd,
                "dominance_pct": "50.00",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.coin.refresh_from_db()
        self.assertEqual(self.coin.name, "Bitcoin Updated")

    def test_position_edit_link_not_coin_link(self):
        position = Position.objects.create(
            coin=self.coin,
            quantity=Decimal("1"),
            avg_price_usd=Decimal("40000"),
        )
        response = self.client.get(reverse("admin:crypto_position_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Изменить")
        self.assertContains(
            response,
            reverse("admin:crypto_position_change", args=[position.pk]),
        )

        response = self.client.post(
            reverse("admin:crypto_position_change", args=[position.pk]),
            {
                "coin": self.coin.pk,
                "quantity": "3.5",
                "avg_price_usd": "41000.00",
            },
        )
        self.assertEqual(response.status_code, 302)
        position.refresh_from_db()
        self.assertEqual(position.quantity, Decimal("3.5"))

    def test_trade_edit_via_change_form(self):
        trade = Trade.objects.create(
            coin=self.coin,
            quote_symbol="USDT",
            side=Trade.Side.BUY,
            status=Trade.Status.FILLED,
            price_usd=Decimal("50000"),
            amount=Decimal("0.1"),
            executed_at=timezone.now(),
        )
        url = reverse("admin:crypto_trade_change", args=[trade.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        executed = timezone.localtime(trade.executed_at)
        response = self.client.post(
            url,
            {
                "coin": self.coin.pk,
                "quote_symbol": "USDT",
                "executed_at_0": executed.date().isoformat(),
                "executed_at_1": executed.strftime("%H:%M:%S"),
                "side": Trade.Side.SELL,
                "status": Trade.Status.FILLED,
                "price_usd": "50500.00",
                "amount": "0.2",
            },
        )
        self.assertEqual(response.status_code, 302)
        trade.refresh_from_db()
        self.assertEqual(trade.side, Trade.Side.SELL)
        self.assertEqual(trade.amount, Decimal("0.2"))

    def test_trade_row_numbers_after_delete(self):
        trade_old = Trade.objects.create(
            coin=self.coin,
            quote_symbol="USDT",
            side=Trade.Side.BUY,
            status=Trade.Status.FILLED,
            price_usd=Decimal("50000"),
            amount=Decimal("0.1"),
            executed_at=timezone.now() - timezone.timedelta(hours=1),
        )
        trade_new = Trade.objects.create(
            coin=self.coin,
            quote_symbol="USDT",
            side=Trade.Side.BUY,
            status=Trade.Status.FILLED,
            price_usd=Decimal("51000"),
            amount=Decimal("0.2"),
            executed_at=timezone.now(),
        )
        trade_old.delete()

        response = self.client.get(reverse("admin:crypto_trade_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "field-row_number")
        self.assertEqual(Trade.objects.count(), 1)

        changelist = response.context["cl"]
        self.assertEqual(len(changelist.result_list), 1)
        self.assertEqual(changelist.result_list[0]._admin_row_number, 1)
        self.assertEqual(changelist.result_list[0].pk, trade_new.pk)

    def test_history_sequential_numbers(self):
        Trade.objects.create(
            coin=self.coin,
            quote_symbol="USDT",
            side=Trade.Side.BUY,
            status=Trade.Status.FILLED,
            price_usd=Decimal("50000"),
            amount=Decimal("0.1"),
            executed_at=timezone.now(),
        )
        response = self.client.get(reverse("crypto:history"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ">1</div>")

    def test_clear_admin_log(self):
        from django.contrib.admin.models import ADDITION, LogEntry
        from django.contrib.contenttypes.models import ContentType

        LogEntry.objects.log_action(
            user_id=self.admin_user.pk,
            content_type_id=ContentType.objects.get_for_model(Coin).pk,
            object_id=self.coin.pk,
            object_repr=str(self.coin),
            action_flag=ADDITION,
        )
        self.assertEqual(LogEntry.objects.filter(user=self.admin_user).count(), 1)

        response = self.client.post(reverse("admin:clear_log"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(LogEntry.objects.filter(user=self.admin_user).count(), 0)

        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "История пуста")

    def test_admin_index_has_clear_button(self):
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Очистить")
        self.assertContains(response, "метки типа действия")


class DemoBuyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.coin = Coin.objects.create(
            symbol="BTC",
            name="Bitcoin",
            price_usd=Decimal("50000.00"),
        )

    def test_demo_buy_creates_trade_and_position(self):
        from crypto.services import apply_demo_buy

        apply_demo_buy(self.coin, Decimal("0.5"))

        self.assertEqual(Trade.objects.filter(coin=self.coin, side=Trade.Side.BUY).count(), 1)
        position = Position.objects.get(coin=self.coin)
        self.assertEqual(position.quantity, Decimal("0.5"))
        self.assertEqual(position.avg_price_usd, Decimal("50000.00"))

    def test_demo_buy_updates_existing_position(self):
        from crypto.services import apply_demo_buy

        Position.objects.create(
            coin=self.coin,
            quantity=Decimal("1"),
            avg_price_usd=Decimal("40000.00"),
        )
        apply_demo_buy(self.coin, Decimal("1"))

        position = Position.objects.filter(coin=self.coin).first()
        self.assertEqual(position.quantity, Decimal("2"))
        self.assertEqual(position.avg_price_usd, Decimal("45000.00"))
        self.assertEqual(Trade.objects.filter(coin=self.coin).count(), 1)

    def test_buy_coin_view(self):
        response = self.client.post(
            reverse("crypto:buy_coin", args=[self.coin.pk]),
            {"amount": "0.25"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Position.objects.filter(coin=self.coin, quantity=Decimal("0.25")).exists())
        self.assertEqual(Trade.objects.filter(coin=self.coin).count(), 1)

    def test_buy_coin_invalid_amount(self):
        response = self.client.post(
            reverse("crypto:buy_coin", args=[self.coin.pk]),
            {"amount": "0"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Position.objects.filter(coin=self.coin).exists())
