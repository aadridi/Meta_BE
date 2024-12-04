from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User


class ManagerGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class ManagerCreateSerializer(serializers.Serializer):
    username = serializers.CharField()

    def validate_username(self, value):
        if not User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                f"User with username '{value}' does not exist.")
        return value


class DeliveryCrewGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class DeliveryCrewCreateSerializer(serializers.Serializer):
    username = serializers.CharField()

    def validate_username(self, value):
        if not User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                f"User with username '{value}' does not exist.")
        return value


class CategorySerializer (serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']


class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all())
    category_details = CategorySerializer(source='category', read_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured',
                  'category', 'category_details']
        depth = 1


class CartSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField(method_name='calculate_price')
    unit_price = serializers.DecimalField(
        max_digits=6, decimal_places=2, read_only=True)
    menuitem = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all())
    menuitem_details = MenuItemSerializer(
        source='menuitem', read_only=True)

    def calculate_price(self, cart):
        return cart.quantity * cart.unit_price

    def create(self, validated_data):
        menuitem = validated_data.get('menuitem')
        validated_data['unit_price'] = menuitem.price
        validated_data['price'] = validated_data['quantity'] * menuitem.price
        return super().create(validated_data)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'menuitem', 'menuitem_details',
                  'quantity', 'unit_price', 'price']
        # depth = 1


class OrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date']
