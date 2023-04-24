from django.core.validators import RegexValidator
from rest_framework import serializers

from mainApp.models import Product, Basket, Order, OrderItem, User


class ProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    category = serializers.IntegerField(required=False)
    price = serializers.IntegerField(required=False)
    description = serializers.CharField(required=False)
    url = serializers.URLField(required=False)

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'price', 'description', 'url']


class BasketSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False)

    class Meta:
        model = Basket
        fields = ['id', 'user', 'product', 'quantity', 'actual_price']


class RequestBasketSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    user = serializers.IntegerField(required=False)
    quantity = serializers.IntegerField(required=False)
    actual_price = serializers.IntegerField(required=False)
    product_id = serializers.IntegerField(required=False)

    class Meta:
        model = Basket
        fields = ['id', 'product_id', 'user', 'quantity', 'actual_price']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_id', 'address', 'delivery_id']


class OrderItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderResponseSerializer(serializers.ModelSerializer):
    order_items = OrderItemsSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'payment_id', 'address', 'delivery_id', 'total_price', 'order_items']


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['username', 'phone_number']
        extra_kwargs = {
            'phone_number': {
                'validators': [RegexValidator()],
            }
        }


class UserResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'


class AuthorizeResponseSerializer(serializers.Serializer):
    need_reg = serializers.BooleanField()
    send_otp = serializers.BooleanField()


class OTPSerializer(serializers.Serializer):
    otp = serializers.IntegerField()
    phone_number = serializers.CharField()
