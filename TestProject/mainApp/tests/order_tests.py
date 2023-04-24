from rest_framework import status
from rest_framework.test import APITestCase
from mainApp.models import Product, Basket, Order, OrderItem, User
from mainApp.tests.test_utils import is_order_fields_ok, is_order_response_fields_ok


class TestOrders(APITestCase):
    def setUp(self):
        self.user1, create = User.objects.get_or_create(username='test user', phone_number='88005553535')
        self.user2, create = User.objects.get_or_create(username='test user2', phone_number='88005553122')

        self.product1, create = Product.objects.get_or_create(name="test product 1",
                                                              category=11,
                                                              price=1000,
                                                              description="test description 1",
                                                              url="http://127.0.0.1:8000/swagger/")

        self.product2, create = Product.objects.get_or_create(name="test product 2",
                                                              category=12,
                                                              price=500,
                                                              description="test description 2",
                                                              url="http://127.0.0.1:8000/swagger/")

        self.basket1, create = Basket.objects.get_or_create(user=1,
                                                            product=self.product1,
                                                            quantity=1,
                                                            actual_price=self.product1.price)
        self.basket2, create = Basket.objects.get_or_create(user=1,
                                                            product=self.product2,
                                                            quantity=2,
                                                            actual_price=self.product1.price * 2)

        self.order, create = Order.objects.get_or_create(user=2,
                                                         delivery_id=1,
                                                         address="address",
                                                         payment_id=2,
                                                         total_price=self.product1.price * 2)
        self.order_item, create = OrderItem.objects.get_or_create(product=self.product1,
                                                                  quantity=2,
                                                                  actual_price=self.product1.price * 2,
                                                                  order=self.order)

    def test_make_order(self):
        data = {'delivery_id': 1, 'address': 'test address', 'payment_id': 2}
        response = self.client.post("/order/", data, format='json', headers={'token': self.user1.token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        order_dict = {'user': 1, 'delivery_id': 1, 'address': 'test address', 'payment_id': 2,
                      'total_price': self.basket1.actual_price + self.basket2.actual_price,
                      'items': [{'product': self.basket1.product, 'quantity': 1,
                                 'actual_price': self.basket1.actual_price},
                                {'product': self.basket2.product, 'quantity': 2,
                                 'actual_price': self.basket2.actual_price}]}
        self.assertTrue(
            is_order_response_fields_ok(data, **order_dict))
        orders = Order.objects.filter(user=1)
        list(list(orders)[0].order_items.all())
        order_items = OrderItem.objects.filter(order=orders[0]).values()
        self.assertTrue(is_order_fields_ok(orders[0], order_items, **order_dict))
        self.assertFalse(Basket.objects.filter(user=1).values())

    def test_make_order_with_no_baskets(self):
        data = {'delivery_id': 1, 'address': 'test address', 'payment_id': 2}
        response = self.client.post("/order/", data, format='json', headers={'token': self.user2.token})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, 'no baskets')

    def test_get_orders(self):
        response = self.client.get("/order/", format='json', headers={'token': self.user2.token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        dict = {'user': 2, 'delivery_id': 1, 'address': 'address', 'payment_id': 2,
                'total_price': self.product1.price * 2,
                'items': [{'product': self.product1, 'quantity': 2,
                           'actual_price': self.product1.price * 2}]}
        self.assertTrue(
            is_order_response_fields_ok(data[0], **dict))
