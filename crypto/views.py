from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.db.models.deletion import ProtectedError

from .forms import CoinForm, PositionForm, TradeForm
from .models import Coin, Position, Trade


def dashboard(request):
    crypto_data = []
    for coin in Coin.objects.all():
        crypto_data.append(
            {
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


def trade_history(request):
    trades = []
    for t in Trade.objects.select_related("coin").all():
        trades.append(
            {
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
    for p in Position.objects.select_related("coin").all():
        value = p.value_usd
        pnl = p.pnl_usd
        equity += float(value)
        positions.append(
            {
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
        {"label": "Сделок за 30 дней", "value": str(trades_30d), "hint": "из базы данных"},
        {"label": "Исполнено / отменено", "value": f"{filled} / {cancelled}", "hint": "статусы сделок"},
        {"label": "Активов в портфеле", "value": str(Position.objects.count()), "hint": "позиции"},
        {"label": "Эквити (оценка)", "value": f"{equity:,.2f} $".replace(",", " "), "hint": "sum(qty * price)"},
    ]

    allocations = []
    total_value = equity if equity > 0 else 0
    for p in Position.objects.select_related("coin").all():
        v = float(p.value_usd)
        pct = int(round((v / total_value) * 100)) if total_value else 0
        allocations.append({"name": p.coin.symbol, "pct": pct})

    notes = [
        "Эта страница уже читает данные из БД. Следующий шаг — добавить графики (Chart.js) и фильтры.",
        "Win‑rate и RR можно считать по сделкам, если хранить цену входа/выхода и комиссии.",
    ]
    return render(
        request,
        "crypto/analytics.html",
        {"kpis": kpis, "allocations": allocations, "notes": notes},
    )


# ---- CRUD: Coins ----


def coin_list(request):
    coins = Coin.objects.all()
    return render(request, "crypto/coins/list.html", {"coins": coins})


def coin_create(request):
    if request.method == "POST":
        form = CoinForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("crypto:coin_list")
    else:
        form = CoinForm()
    return render(request, "crypto/coins/form.html", {"form": form, "mode": "create"})


def coin_update(request, pk: int):
    coin = get_object_or_404(Coin, pk=pk)
    if request.method == "POST":
        form = CoinForm(request.POST, instance=coin)
        if form.is_valid():
            form.save()
            return redirect("crypto:coin_list")
    else:
        form = CoinForm(instance=coin)
    return render(request, "crypto/coins/form.html", {"form": form, "mode": "update", "coin": coin})


def coin_delete(request, pk: int):
    coin = get_object_or_404(Coin, pk=pk)
    if request.method == "POST":
        try:
            coin.delete()
            return redirect("crypto:coin_list")
        except ProtectedError:
            # Если монета используется в позициях или сделках (on_delete=PROTECT),
            # то Django запретит удаление — вместо падения показываем страницу подтверждения.
            return render(
                request,
                "crypto/coins/confirm_delete.html",
                {"coin": coin, "error": "Удаление невозможно: монета используется в позициях или сделках."},
            )
    return render(request, "crypto/coins/confirm_delete.html", {"coin": coin})


# ---- CRUD: Trades ----


def trade_list(request):
    trades = Trade.objects.select_related("coin").all()
    return render(request, "crypto/trades/list.html", {"trades": trades})


def trade_create(request):
    if request.method == "POST":
        form = TradeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("crypto:trade_list")
    else:
        form = TradeForm()
    return render(request, "crypto/trades/form.html", {"form": form, "mode": "create"})


def trade_update(request, pk: int):
    trade = get_object_or_404(Trade, pk=pk)
    if request.method == "POST":
        form = TradeForm(request.POST, instance=trade)
        if form.is_valid():
            form.save()
            return redirect("crypto:trade_list")
    else:
        form = TradeForm(instance=trade)
    return render(request, "crypto/trades/form.html", {"form": form, "mode": "update", "trade": trade})


def trade_delete(request, pk: int):
    trade = get_object_or_404(Trade, pk=pk)
    if request.method == "POST":
        trade.delete()
        return redirect("crypto:trade_list")
    return render(request, "crypto/trades/confirm_delete.html", {"trade": trade})


# ---- CRUD: Positions ----


def position_list(request):
    positions = Position.objects.select_related("coin").all()
    total_value = 0
    for p in positions:
        total_value += float(p.value_usd)
    return render(
        request,
        "crypto/positions/list.html",
        {"positions": positions, "total_value": f"{total_value:,.2f} $".replace(",", " ")},
    )


def position_create(request):
    if request.method == "POST":
        form = PositionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("crypto:position_list")
    else:
        form = PositionForm()
    return render(request, "crypto/positions/form.html", {"form": form, "mode": "create"})


def position_update(request, pk: int):
    position = get_object_or_404(Position, pk=pk)
    if request.method == "POST":
        form = PositionForm(request.POST, instance=position)
        if form.is_valid():
            form.save()
            return redirect("crypto:position_list")
    else:
        form = PositionForm(instance=position)
    return render(
        request,
        "crypto/positions/form.html",
        {"form": form, "mode": "update", "position": position},
    )


def position_delete(request, pk: int):
    position = get_object_or_404(Position, pk=pk)
    if request.method == "POST":
        position.delete()
        return redirect("crypto:position_list")
    return render(request, "crypto/positions/confirm_delete.html", {"position": position})

