from django.urls import path

from . import views

app_name = "salon"

urlpatterns = [
    path("", views.catalog, name="catalog"),
    path("buy/<int:product_id>/", views.buy_product, name="buy_product"),
    path("orders/", views.orders, name="orders"),
    path("warehouse/", views.warehouse, name="warehouse"),
    path("analytics/", views.analytics, name="analytics"),
    path("services/", views.services_page, name="services"),
    path("services/<int:service_id>/request/", views.request_service, name="request_service"),
    path("about/", views.about, name="about"),
]
