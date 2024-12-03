from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("menu-items/", views.MenuItemsView.as_view(), name="menu-items"),
    path("menu-items/<int:pk>/", views.SingleMenuItemView.as_view(),
         name="single-menu-item"),
    path("cart/menu-items/", views.CartView.as_view(), name="cart"),
    path("orders/", views.OrdersView.as_view(), name="orders"),
    path("groups/manager/users/", views.ManagersView.as_view(), name="managers"),
]
