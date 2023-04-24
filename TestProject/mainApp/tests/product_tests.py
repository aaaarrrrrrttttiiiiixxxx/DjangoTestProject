from rest_framework import status
from rest_framework.test import APITestCase
from mainApp.models import Product
from mainApp.tests.test_utils import is_product_fields_equal


class TestProducts(APITestCase):
    def setUp(self):
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
        self.product3, create = Product.objects.get_or_create(name="test product 3",
                                                              category=11,
                                                              price=1300,
                                                              description="test description 3",
                                                              url="http://127.0.0.1:8000/swagger/")

    def test_get(self):
        response = self.client.get("/products/", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), Product.objects.all().count())
        self.assertTrue(is_product_fields_equal(data[0], self.product1))
        self.assertTrue(is_product_fields_equal(data[1], self.product2))
        self.assertTrue(is_product_fields_equal(data[2], self.product3))

    def test_get_for_category(self):
        data = {'category': 11}
        response = self.client.post("/products/", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertTrue(is_product_fields_equal(data[0], self.product1))
        self.assertTrue(is_product_fields_equal(data[1], self.product3))

    def test_get_for_with_wrong_category(self):
        data = {'category': 111}
        response = self.client.post("/products/", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 0)

    def test_get_for_id(self):
        url = f"/product/?product_id={self.product1.id}"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(is_product_fields_equal(data, self.product1))

    def test_get_with_wrong_id(self):
        url = f"/product/?product_id=11111"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
