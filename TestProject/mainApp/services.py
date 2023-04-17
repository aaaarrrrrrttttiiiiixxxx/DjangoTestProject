from django.db.models import Sum, F

from mainApp.models import Basket, Order, OrderItem, Product


class OrderService:
    def __init__(self, data):
        self.data = data

    def make_order(self):
        order = Order(**self.data)
        baskets = Basket.objects.filter(user=self.data['user'])
        if not baskets:
            return False, None
        total_price = baskets.annotate(sum_items=F('actual_price') * F('quantity')).aggregate(total_price=Sum('sum_items'))['total_price']
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
    def __init__(self, data):
        self.data = data

    def update_basket(self):
        basket = Basket.objects.filter(id=self.data['id'])
        if not basket:
            return False
        basket.quantity = self.data['quantity']
        basket.actual_price = basket.quantity * basket.product.price
        basket.save()
        return True

    def make_basket(self):
        basket = Basket()
        basket.user = self.data['user']
        product = Product.objects.filter(id=self.data['product_id'])
        if not product:
            return False
        basket.product_id = self.data['product_id']
        basket.quantity = self.data['quantity']
        basket.actual_price = basket.quantity * basket.product.price
        basket.save()
        return True
