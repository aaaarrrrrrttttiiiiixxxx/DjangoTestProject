from rest_framework import status
from rest_framework.test import APITestCase
from mainApp.models import Product, Basket, User
from mainApp.tests.test_utils import is_basket_fields_equal, is_basket_fields_ok


class TestBaskets(APITestCase):
    def setUp(self):
        self.user, create = User.objects.get_or_create(username='test user', phone_number='88005553535')

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

    def test_get_for_user(self):
        response = self.client.post("/basket/", format='json', headers={'token': self.user.token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertTrue(is_basket_fields_equal(data[0], self.basket1))
        self.assertTrue(is_basket_fields_equal(data[1], self.basket2))

    def test_get_for_wrong_user(self):
        response = self.client.post("/basket/", format='json', headers={'token': 'oi5ebF4H589HGU9ER5TH5G98R2tJ848gh34'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_basket(self):
        data = {'product_id': self.product1.id, 'quantity': 3}
        response = self.client.post("/addToBasket/", data, format='json', headers={'token': self.user.token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        basket_to_compare = Basket(user=1, product=self.product1, quantity=3, actual_price=self.product1.price * 3)
        self.assertTrue(is_basket_fields_equal(data[2], basket_to_compare))

        basket = Basket.objects.filter(user=1).values()
        self.assertTrue(is_basket_fields_ok(basket[2], 1, self.product1, 3, self.product1.price * 3))

    def test_update_basket(self):
        data = {'id': self.basket1.id, 'quantity': 3}
        response = self.client.put("/basket/", data, format='json', headers={'token': self.user.token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        basket_to_compare = Basket(user=1, product=self.product1, quantity=3, actual_price=self.product1.price * 3)
        self.assertEqual(len(data), 2)
        self.assertTrue(is_basket_fields_equal(data[0], basket_to_compare))
        self.assertTrue(is_basket_fields_equal(data[1], self.basket2))

        basket = Basket.objects.filter(user=1).values()
        self.assertTrue(is_basket_fields_ok(basket[0], 1, self.product1, 3, self.product1.price * 3))

    def test_update_nonexistent_basket(self):
        data = {'id': 11111, 'quantity': 3}
        response = self.client.put("/basket/", data, format='json', headers={'token': self.user.token})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete(self):
        data = {'id': self.basket2.id}
        response = self.client.delete("/basket/", data, format='json', headers={'token': self.user.token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        basket_to_compare = Basket(user=1, product=self.product1, quantity=1, actual_price=self.product1.price * 1)
        self.assertEqual(len(data), 1)
        self.assertTrue(is_basket_fields_equal(data[0], basket_to_compare))

        self.assertFalse(Basket.objects.filter(id=self.basket2.id).values())

    def test_delete_nonexistent_basket(self):
        data = {'id': 11111}
        response = self.client.delete("/basket/", data, format='json', headers={'token': self.user.token})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
