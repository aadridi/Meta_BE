from django.shortcuts import render
from .serializers import MenuItemSerializer, CartSerializer, OrdersSerializer, ManagerGetSerializer, ManagerCreateSerializer
from .models import MenuItem, Cart, Order, OrderItem
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
from .permissions import IsManager


# Create your views here.
class ManagersView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ManagerCreateSerializer
        return ManagerGetSerializer

    def get_queryset(self):
        manager_group = Group.objects.get(name='Manager')
        return manager_group.user_set.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']

        user = User.objects.get(username=username)
        manager_group, created = Group.objects.get_or_create(name='Manager')
        if user in manager_group.user_set.all():
            return Response(
                {"message": f"User '{username}' is already a manager"},
                status=status.HTTP_200_OK,
            )
        manager_group.user_set.add(user)

        return Response(
            {"message": f"User '{username}' has been added to the Manager group"},
            status=status.HTTP_201_CREATED,
        )


class DeliveryCrewView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ManagerCreateSerializer
        return ManagerGetSerializer

    def get_queryset(self):
        delivery_team_group = Group.objects.get(name='Delivery Team')
        return delivery_team_group.user_set.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']

        user = User.objects.get(username=username)
        delivery_team_group, created = Group.objects.get_or_create(
            name='Delivery Team')
        if user in delivery_team_group.user_set.all():
            return Response(
                {"message": f"User '{username}' is already part of the delivery team"},
                status=status.HTTP_200_OK,
            )
        delivery_team_group.user_set.add(user)

        return Response(
            {"message": f"User '{username}' has been added to the Manager group"},
            status=status.HTTP_201_CREATED,
        )


class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if not request.user.has_perm('LittleLemonAPI.add_menuitem'):
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)


class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        if not request.user.has_perm('LittleLemonAPI.delete_menuitem'):
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class CartView(generics.ListCreateAPIView, generics.DestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        user = request.user
        Cart.objects.filter(user=user).delete()
        return Response({"success": "Your cart has been emptied."}, status=status.HTTP_204_NO_CONTENT)


class OrdersView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrdersSerializer
    permission_classes = [permissions.IsAuthenticated]
