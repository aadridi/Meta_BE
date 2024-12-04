from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("menu-items/", views.MenuItemsView.as_view(), name="menu-items"),
    path("menu-items/<int:pk>/", views.SingleMenuItemView.as_view(),
         name="single-menu-item"),
    path("cart/menu-items/", views.CartView.as_view(), name="cart"),
    path("orders/", views.OrdersView.as_view(), name="orders"),
    path("orders/<int:pk>/", views.SingleOrderView.as_view(), name="single-order"),
    path("groups/manager/users/", views.ManagersView.as_view(), name="managers"),
    path("groups/delivery-crew/users/",
         views.DeliveryCrewView.as_view(), name="delivery-crew"),
    path("groups/manager/users/<int:pk>/",
         views.DeleteManagerView.as_view(), name="delete-manager"),
    path("groups/delivery-crew/users/<int:pk>/",
         views.DeleteDeliveryCrewView.as_view(), name="delete-delivery-crew")
]
