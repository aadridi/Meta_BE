from rest_framework import serializers
from .models import Category, MenuItem, Cart


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
    class Meta:
        model = Cart
        fields = ['id', 'user', 'menuitem', 'quantity', 'unit_price', 'price']
        depth = 1
