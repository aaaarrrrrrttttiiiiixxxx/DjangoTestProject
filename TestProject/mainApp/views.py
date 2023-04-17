from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from mainApp.models import Product, Basket, Order

from mainApp.serializers import ProductSerializer, BasketSerializer, RequestBasketSerializer, OrderSerializer, \
    OrderResponseSerializer
from mainApp.services import OrderService, BasketService


class ProductsPage(APIView):
    @swagger_auto_schema(
        operation_summary="Получение списка всех продуктов",
        responses={200: ProductSerializer(many=True), 500: "Серверная ошибка"},
    )
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return JsonResponse(serializer.data, safe=False)

    @swagger_auto_schema(
        operation_summary="Получение продуктов по категории",
        responses={200: ProductSerializer(many=True), 400: 'ошибочный запрос', 500: "Серверная ошибка"},
        request_body=ProductSerializer
    )
    def post(self, request):
        request_serializer = ProductSerializer(data=request.data)
        if request_serializer.is_valid():
            category = request_serializer.validated_data['category']
            products = Product.objects.filter(category=category)
            serializer = ProductSerializer(products, many=True)
            return JsonResponse(serializer.data, safe=False)
        response = Response()
        response.status_code = 400
        response.data = request_serializer.errors
        return response


class ProductPage(APIView):
    @swagger_auto_schema(
        operation_summary="Поучение продукта",
        responses={200: ProductSerializer(many=False), 400: 'ошибочный запрос',  500: "Серверная ошибка"},
        manual_parameters=[openapi.Parameter('product_id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER)]
    )
    def get(self, request):
        product_id = request.GET.get('product_id')
        product = get_object_or_404(Product, pk=product_id)
        serializer = ProductSerializer(product)
        return JsonResponse(serializer.data, safe=False)


class BasketPage(APIView):
    @swagger_auto_schema(
        operation_summary="Поучение корзин продуктов пользователя",
        responses={200: BasketSerializer(many=True), 400: 'ошибочный запрос', 500: "Серверная ошибка"},
        request_body=RequestBasketSerializer
    )
    def post(self, request):
        request_serializer = RequestBasketSerializer(data=request.data)
        if request_serializer.is_valid():
            user_id = request_serializer.validated_data['user']
            baskets = Basket.objects.filter(user=user_id)
            serializer = BasketSerializer(baskets, many=True)
            return JsonResponse(serializer.data, safe=False)
        response = Response()
        response.status_code = 400
        response.data = request_serializer.errors
        return response

    @swagger_auto_schema(
        operation_summary="Изменение продукта в корзине",
        responses={200: BasketSerializer(many=True), 400: 'ошибочный запрос', 500: "Серверная ошибка"},
        request_body=RequestBasketSerializer
    )
    def put(self, request):
        request_serializer = RequestBasketSerializer(data=request.data)
        if request_serializer.is_valid():
            service = BasketService(request_serializer.validated_data)
            ok = service.update_basket()
            if not ok:
                response = Response()
                response.status_code = 400
                response.data = 'no such basket'
                return response
            user_id = Basket.objects.get(id=request_serializer.validated_data['id']).user
            baskets = Basket.objects.filter(user=user_id)
            serializer = BasketSerializer(baskets, many=True)
            return JsonResponse(serializer.data, safe=False)
        response = Response()
        response.status_code = 400
        response.data = request_serializer.errors
        return response

    @swagger_auto_schema(
        operation_summary="Удаление продукта из корзины",
        responses={200: BasketSerializer(many=True), 400: 'ошибочный запрос', 500: "Серверная ошибка"},
        request_body=RequestBasketSerializer
    )
    def delete(self, request):
        request_serializer = RequestBasketSerializer(data=request.data)
        if request_serializer.is_valid():
            basket_id = request_serializer.validated_data['id']
            basket = Basket.objects.filter(id=basket_id)
            if not basket:
                response = Response()
                response.status_code = 400
                response.data = 'no such basket'
                return response
            user_id = basket.user
            basket.delete()
            baskets = Basket.objects.filter(user=user_id)
            serializer = BasketSerializer(baskets, many=True)
            return JsonResponse(serializer.data, safe=False)
        response = Response()
        response.status_code = 400
        response.data = request_serializer.errors
        return response


class BasketPagePost(APIView):
    @swagger_auto_schema(
        operation_summary="добавление товара в корзину",
        responses={200: BasketSerializer(many=True), 400: 'ошибочный запрос', 500: "Серверная ошибка"},
        request_body=RequestBasketSerializer
    )
    def post(self, request):
        request_serializer = RequestBasketSerializer(data=request.data)
        if request_serializer.is_valid():
            service = BasketService(request_serializer.validated_data)
            ok = service.make_basket()
            if not ok:
                response = Response()
                response.status_code = 400
                response.data = 'no such product'
                return response
            user_id = request_serializer.validated_data['user']
            baskets = Basket.objects.filter(user=user_id)
            serializer = BasketSerializer(baskets, many=True)
            return JsonResponse(serializer.data, safe=False)
        response = Response()
        response.status_code = 400
        response.data = request_serializer.errors
        return response


class OrderPage(APIView):
    @swagger_auto_schema(
        operation_summary="Создание заказа",
        responses={200: OrderResponseSerializer(), 400: 'ошибочный запрос', 500: "Серверная ошибка"},
        request_body=OrderSerializer
    )
    def post(self, request):
        request_serializer = OrderSerializer(data=request.data)
        if request_serializer.is_valid():
            service = OrderService(request_serializer.validated_data)
            ok, order = service.make_order()
            if not ok:
                response = Response()
                response.status_code = 400
                response.data = 'no baskets'
                return response
            serializer = OrderResponseSerializer(order)
            return JsonResponse(serializer.data, safe=False)
        response = Response()
        response.status_code = 400
        response.data = request_serializer.errors
        return response

    @swagger_auto_schema(
        operation_summary="Поучение всех заказов пользователя",
        responses={200: OrderResponseSerializer(many=True), 400: 'ошибочный запрос', 500: "Серверная ошибка"},
        manual_parameters=[openapi.Parameter('user', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER)]
    )
    def get(self, request):
        request_serializer = OrderSerializer(data=request.GET)
        if request_serializer.is_valid():
            orders = Order.objects.filter(user=request_serializer.validated_data['user'])
            serializer = OrderResponseSerializer(orders, many=True)
            return JsonResponse(serializer.data, safe=False)
        response = Response()
        response.status_code = 400
        response.data = request_serializer.errors
        return response
