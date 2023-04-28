import base64
import secrets

from django.core.validators import RegexValidator
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=20, blank=False)
    category = models.IntegerField()
    price = models.IntegerField(default=0)
    description = models.CharField(max_length=500)
    url = models.URLField()

    def __str__(self):
        return f'id: {self.id} name: {self.name} category: {self.category}'


class Basket(models.Model):
    user = models.IntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_cart')
    quantity = models.IntegerField()
    actual_price = models.IntegerField()

    def __str__(self):
        return f'id: {self.id} user: {self.user} product: {self.product} quantity: {self.quantity} actual_price: ' \
               f'{self.actual_price}'


class Order(models.Model):
    user = models.IntegerField()
    delivery_id = models.IntegerField()
    address = models.CharField(max_length=50)
    payment_id = models.IntegerField()
    total_price = models.IntegerField()

    def __str__(self):
        return f'id: {self.id} user: {self.user} delivery_id: {self.delivery_id} address: {self.address} payment_id: ' \
               f'{self.payment_id}'


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_order')
    quantity = models.IntegerField()
    actual_price = models.IntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')

    def __str__(self):
        return f'id: {self.id} product: {self.product} quantity: {self.quantity} actual_price: {self.actual_price}'


def _create_token():
    return base64.b64encode(secrets.token_bytes()).decode('utf8')


class User(models.Model):
    username = models.CharField(max_length=50)
    phone_number_regex = RegexValidator(regex=r"^\+?1?\d{11,12}$")
    phone_number = models.CharField(validators=[phone_number_regex], max_length=16, unique=True)
    token = models.CharField(max_length=64, default=_create_token)

    def __str__(self):
        return f'id: {self.id} {self.username} {self.phone_number} {self.token}'


class Image(models.Model):
    url = models.URLField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')

    def __str__(self):
        return f'id: {self.id} url: {self.url}'
