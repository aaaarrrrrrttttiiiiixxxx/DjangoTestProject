from django.contrib import admin

from mainApp.models import Product, Basket, Order, User, OrderItem, Image

admin.site.register(Product)
admin.site.register(Basket)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(User)
admin.site.register(Image)


