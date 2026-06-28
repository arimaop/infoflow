from django.urls import path

from . import views

app_name = "crypto"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("buy/<int:coin_id>/", views.buy_coin, name="buy_coin"),
    path("history/", views.trade_history, name="history"),
    path("portfolio/", views.portfolio, name="portfolio"),
    path("analytics/", views.analytics, name="analytics"),
    path("chronicle/", views.crypto_chronicle, name="chronicle"),
]
