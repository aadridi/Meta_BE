from .serializers import MenuItemSerializer, CartSerializer, OrderSerializer, OrderItemSerializer, ManagerGetSerializer, ManagerCreateSerializer
from .models import MenuItem, Cart, Order, OrderItem
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
from .permissions import IsManager, IsCustomer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
# from django.core.exceptions import PermissionDenied


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
        manager_group = Group.objects.get_or_create(name='Manager')
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
        delivery_team_group = Group.objects.get_or_create(
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


class DeleteManagerView(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        manager_group = Group.objects.get(name="Manager")
        if user not in manager_group.user_set.all():
            return Response(
                {"error": f"User '{user.username}' is not in the Manager group"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        manager_group.user_set.remove(user)
        return Response(
            {"message": f"User '{user.username}' has been removed from the Manager group"},
            status=status.HTTP_200_OK,
        )


class DeleteDeliveryCrewView(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        delivery_crew_group = Group.objects.get(name="Delivery Crew")
        if user not in delivery_crew_group.user_set.all():
            return Response(
                {"error": f"User '{user.username}' is not in the Delivery Crew group"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        delivery_crew_group.user_set.remove(user)
        return Response({"message": f"User '{user.username}' has been removed from the Delivery Crew group"},
                        status=status.HTTP_200_OK,
                        )


class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['category', 'price']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'name']

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


class CartView(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        user = request.user
        Cart.objects.filter(user=user).delete()
        return Response({"success": "Your cart has been emptied."}, status=status.HTTP_204_NO_CONTENT)


class OrdersView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'delivery_crew', 'user', 'date']
    ordering_fields = ['total', 'date']

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        elif user.groups.filter(name='Delivery Crew').exists():
            return Order.objects.filter(delivery_crew=user)
        else:
            return Order.objects.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        cart_items = Cart.objects.filter(user=user)

        if not cart_items.exists():
            raise serializers.ValidationError("Your cart is empty.")

        order = serializer.save(user=user, total=sum(
            item.price for item in cart_items))
        order_items = [
            OrderItem(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price
            )
            for item in cart_items
        ]
        OrderItem.objects.bulk_create(order_items)
        cart_items.delete()
        return order


class SingleOrderView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        elif user.groups.filter(name='Delivery Crew').exists():
            return Order.objects.filter(delivery_crew=user)
        else:
            return Order.objects.filter(user=user)

    def perform_update(self, serializer):
        user = self.request.user

        if user.groups.filter(name='Manager').exists():
            serializer.save()
        elif user.groups.filter(name='Delivery Crew').exists():
            if 'status' in serializer.validated_data and len(serializer.validated_data) == 1:
                serializer.save()
            else:
                raise PermissionDenied("You can only update the status.")
        else:
            raise PermissionDenied(
                "You do not have permission to update this order.")

    def destroy(self, request, *args, **kwargs):
        user = request.user

        if user.groups.filter(name='Manager').exists():
            return super().destroy(request, *args, **kwargs)
        raise PermissionDenied("Only managers can delete orders.")
