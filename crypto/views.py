from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Coin, Position, Trade
from .services import apply_demo_buy


def dashboard(request):
    crypto_data = []
    for coin in Coin.objects.all():
        crypto_data.append(
            {
                "id": coin.id,
                "name": coin.name,
                "symbol": coin.symbol,
                "price": f"{coin.price_usd:,.2f} $".replace(",", " "),
                "change_24h": f"{coin.change_24h_pct:+.2f}%",
                "market_cap": f"{coin.market_cap_usd:,} $".replace(",", " "),
                "volume_24h": f"{coin.volume_24h_usd:,} $".replace(",", " "),
                "dominance": f"{coin.dominance_pct:.2f}%",
                "tagline": coin.tagline,
            }
        )
    context = {
        "crypto_data": crypto_data,
    }
    return render(request, "crypto/dashboard.html", context)


@require_POST
def buy_coin(request, coin_id: int):
    coin = get_object_or_404(Coin, pk=coin_id)
    raw_amount = request.POST.get("amount", "").strip().replace(",", ".")

    try:
        amount = Decimal(raw_amount)
        apply_demo_buy(coin, amount)
    except (InvalidOperation, ValueError):
        messages.error(request, "Укажите корректное количество больше нуля.")
        return redirect("crypto:dashboard")

    total_usd = coin.price_usd * amount
    messages.success(
        request,
        f"Условная покупка: {amount.normalize()} {coin.symbol} "
        f"по {coin.price_usd:,.2f} $ (≈ {total_usd:,.2f} $). "
        f"Позиция добавлена в портфель.",
    )
    return redirect("crypto:portfolio")


def trade_history(request):
    trades = []
    for index, t in enumerate(Trade.objects.select_related("coin").all(), start=1):
        trades.append(
            {
                "num": index,
                "id": t.id,
                "time": timezone.localtime(t.executed_at).strftime("%d.%m %H:%M"),
                "pair": f"{t.coin.symbol}/{t.quote_symbol}",
                "side": t.side,
                "price": f"{t.price_usd:,.2f} $".replace(",", " "),
                "amount": f"{t.amount.normalize()} {t.coin.symbol}",
                "status": t.get_status_display(),
            }
        )
    return render(request, "crypto/history.html", {"trades": trades})


def portfolio(request):
    positions = []
    equity = 0
    for index, p in enumerate(Position.objects.select_related("coin").order_by("coin__symbol"), start=1):
        value = p.value_usd
        pnl = p.pnl_usd
        equity += float(value)
        positions.append(
            {
                "num": index,
                "id": p.id,
                "asset": p.coin.symbol,
                "name": p.coin.name,
                "qty": f"{p.quantity.normalize()}",
                "avg_price": f"{p.avg_price_usd:,.2f} $".replace(",", " "),
                "value": f"{value:,.2f} $".replace(",", " "),
                "pnl": f"{pnl:+,.2f} $".replace(",", " "),
                "pnl_pct": f"{p.pnl_pct:+.2f}%",
            }
        )

    summary = {
        "equity": f"{equity:,.2f} $".replace(",", " "),
        "day_change": "—",
        "risk_level": "Умеренный",
    }
    return render(
        request,
        "crypto/portfolio.html",
        {"positions": positions, "summary": summary},
    )


def analytics(request):
    trades_30d = Trade.objects.filter(executed_at__gte=timezone.now() - timezone.timedelta(days=30)).count()
    filled = Trade.objects.filter(status=Trade.Status.FILLED).count()
    cancelled = Trade.objects.filter(status=Trade.Status.CANCELLED).count()

    equity = 0
    for p in Position.objects.select_related("coin").all():
        equity += float(p.value_usd)

    kpis = [
        {"label": "Сделок за 30 дней", "value": str(trades_30d), "hint": "история сделок"},
        {"label": "Исполнено / отменено", "value": f"{filled} / {cancelled}", "hint": "статусы сделок"},
        {"label": "Активов в портфеле", "value": str(Position.objects.count()), "hint": "позиции"},
        {"label": "Эквити (оценка)", "value": f"{equity:,.2f} $".replace(",", " "), "hint": "sum(qty * price)"},
    ]

    allocations = []
    total_value = equity if equity > 0 else 0
    for p in Position.objects.select_related("coin").order_by("coin__symbol"):
        v = float(p.value_usd)
        pct = int(round((v / total_value) * 100)) if total_value else 0
        allocations.append({"name": p.coin.symbol, "pct": pct})

    notes = [
        "Покупки с «Обзора рынка» автоматически попадают в портфель, историю и KPI.",
        "Вывод средств и реальная торговля через API — запланированы на следующий этап.",
    ]
    return render(
        request,
        "crypto/analytics.html",
        {"kpis": kpis, "allocations": allocations, "notes": notes},
    )


def crypto_chronicle(request):
    return render(request, "crypto/chronicle.html")
