from django.db.models import Sum
from django.shortcuts import get_object_or_404

from mainApp.models import Basket, Order, OrderItem, Product, User
from mainApp.serializers import AuthorizeResponseSerializer


class OrderService:
    def __init__(self, data, user):
        self.data = data
        self.user = user

    def make_order(self):
        order = Order(**self.data)
        order.user = self.user
        baskets = Basket.objects.filter(user=self.user)
        if not baskets:
            return False, None
        total_price = baskets.aggregate(total_price=Sum('actual_price'))['total_price']
        order.total_price = total_price
        order.save()
        for basket in baskets:
            order_item = OrderItem()
            order_item.product = basket.product
            order_item.quantity = basket.quantity
            order_item.actual_price = basket.actual_price
            order_item.order = order
            order_item.save()
        baskets.delete()
        return True, order


class BasketService:
    def __init__(self, data, user=None):
        self.data = data
        self.user = user

    def update_basket(self):
        basket = get_object_or_404(Basket, pk=self.data['id'])

        basket.quantity = self.data['quantity']
        basket.actual_price = basket.quantity * basket.product.price
        basket.save()

    def make_basket(self):
        basket = Basket()
        # basket.user = self.data['user']
        basket.user = self.user
        product = Product.objects.filter(id=self.data['product_id'])
        if not product:
            return False
        basket.product_id = self.data['product_id']
        basket.quantity = self.data['quantity']
        basket.actual_price = basket.quantity * basket.product.price
        basket.save()
        return True


class AuthorizationService:
    def __init__(self, data):
        self.data = data

    def authorize(self):
        user = User.objects.filter(phone_number=self.data['phone_number'])
        return AuthorizeResponseSerializer({'send_otp': user, 'need_reg': not user})

    def create_user(self):
        user, created = User.objects.get_or_create(phone_number=self.data['phone_number'])
        user.username = self.data['username']
        user.save()
        return AuthorizeResponseSerializer({'send_otp': True, 'need_reg': False})
