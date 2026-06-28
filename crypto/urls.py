from django.urls import path

from . import views

app_name = "crypto"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("history/", views.trade_history, name="history"),
    path("portfolio/", views.portfolio, name="portfolio"),
    path("analytics/", views.analytics, name="analytics"),

    path("manage/coins/", views.coin_list, name="coin_list"),
    path("manage/coins/new/", views.coin_create, name="coin_create"),
    path("manage/coins/<int:pk>/edit/", views.coin_update, name="coin_update"),
    path("manage/coins/<int:pk>/delete/", views.coin_delete, name="coin_delete"),

    path("manage/trades/", views.trade_list, name="trade_list"),
    path("manage/trades/new/", views.trade_create, name="trade_create"),
    path("manage/trades/<int:pk>/edit/", views.trade_update, name="trade_update"),
    path("manage/trades/<int:pk>/delete/", views.trade_delete, name="trade_delete"),

    path("manage/positions/", views.position_list, name="position_list"),
    path("manage/positions/new/", views.position_create, name="position_create"),
    path("manage/positions/<int:pk>/edit/", views.position_update, name="position_update"),
    path("manage/positions/<int:pk>/delete/", views.position_delete, name="position_delete"),
]

