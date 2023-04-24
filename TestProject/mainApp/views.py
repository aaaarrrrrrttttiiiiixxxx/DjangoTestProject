from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from mainApp.models import Product, Basket, Order, User

from mainApp.serializers import ProductSerializer, BasketSerializer, RequestBasketSerializer, OrderSerializer, \
    OrderResponseSerializer, UserSerializer, AuthorizeResponseSerializer, OTPSerializer, UserResponseSerializer
from mainApp.services import OrderService, BasketService, AuthorizationService


def get_header_params():
    header_param = openapi.Parameter('token', openapi.IN_HEADER, description="token", type=openapi.IN_HEADER)
    return [header_param]


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
        responses={200: ProductSerializer(many=False), 400: 'ошибочный запрос', 500: "Серверная ошибка"},
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
        request_body=RequestBasketSerializer,
        manual_parameters=get_header_params()
    )
    def post(self, request):
        request_serializer = RequestBasketSerializer(data=request.data)
        if request_serializer.is_valid():
            user = User.objects.filter(token=request.headers.get('token'))
            if not user:
                return HttpResponse('Unauthorized', status=401)
            user_id = user.first().id
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
        request_body=RequestBasketSerializer,
        manual_parameters=get_header_params()
    )
    def put(self, request):
        request_serializer = RequestBasketSerializer(data=request.data)
        if request_serializer.is_valid():
            data = request_serializer.validated_data
            user = User.objects.filter(token=request.headers.get('token'))
            if not user:
                return HttpResponse('Unauthorized', status=401)
            service = BasketService(data)
            service.update_basket()
            user_id = user.first().id
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
        request_body=RequestBasketSerializer,
        manual_parameters=get_header_params()
    )
    def delete(self, request):
        request_serializer = RequestBasketSerializer(data=request.data)
        if request_serializer.is_valid():
            data = request_serializer.validated_data
            user = User.objects.filter(token=request.headers.get('token'))
            if not user:
                return HttpResponse('Unauthorized', status=401)
            basket_id = data['id']
            basket = get_object_or_404(Basket, pk=basket_id)
            user_id = user.first().id
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
        request_body=RequestBasketSerializer,
        manual_parameters=get_header_params()
    )
    def post(self, request):
        request_serializer = RequestBasketSerializer(data=request.data)
        if request_serializer.is_valid():
            data = request_serializer.validated_data
            user = User.objects.filter(token=request.headers.get('token'))
            if not user:
                return HttpResponse('Unauthorized', status=401)
            service = BasketService(data, user.first().id)
            ok = service.make_basket()
            if not ok:
                response = Response()
                response.status_code = 400
                response.data = 'no such product'
                return response
            user_id = user.first().id
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
        request_body=OrderSerializer,
        manual_parameters=get_header_params()
    )
    def post(self, request):
        request_serializer = OrderSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        data = request_serializer.validated_data
        user = User.objects.filter(token=request.headers.get('token'))
        if not user:
            return HttpResponse('Unauthorized', status=401)
        service = OrderService(data, user.first().id)
        ok, order = service.make_order()
        if not ok:
            response = Response()
            response.status_code = 400
            response.data = 'no baskets'
            return response
        serializer = OrderResponseSerializer(order)
        return JsonResponse(serializer.data, safe=False)

    @swagger_auto_schema(
        operation_summary="Поучение всех заказов пользователя",
        responses={200: OrderResponseSerializer(many=True), 400: 'ошибочный запрос', 500: "Серверная ошибка"},
        manual_parameters=[openapi.Parameter('user', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
                           openapi.Parameter('token', openapi.IN_HEADER, description="token", type=openapi.IN_HEADER)]
    )
    def get(self, request):
        user = User.objects.filter(token=request.headers.get('token')).first()
        if not user:
            return HttpResponse('Unauthorized', status=401)
        orders = Order.objects.prefetch_related('order_items').filter(
            user=user.id)
        serializer = OrderResponseSerializer(orders, many=True)
        return JsonResponse(serializer.data, safe=False)


class AuthorizePage(APIView):
    @swagger_auto_schema(
        operation_summary="авторизация",
        responses={200: AuthorizeResponseSerializer(), 400: 'ошибочный запрос', 500: "Серверная ошибка"},
        request_body=UserSerializer
    )
    def post(self, request):
        request_serializer = UserSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        service = AuthorizationService(request_serializer.validated_data)
        return JsonResponse(service.authorize().data, safe=False)

    @swagger_auto_schema(
        operation_summary="ввод имени",
        responses={200: AuthorizeResponseSerializer(), 400: 'ошибочный запрос', 500: "Серверная ошибка"},
        request_body=UserSerializer
    )
    def put(self, request):
        request_serializer = UserSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        service = AuthorizationService(request_serializer.validated_data)
        return JsonResponse(service.create_user().data, safe=False)


class ConfirmAuthorizationPage(APIView):
    @swagger_auto_schema(
        operation_summary="проверка кода",
        responses={200: UserResponseSerializer(), 400: 'ошибочный запрос', 500: "Серверная ошибка"},
        request_body=OTPSerializer
    )
    def post(self, request):
        request_serializer = OTPSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        data = request_serializer.validated_data
        if data['otp'] != 777:
            response = Response()
            response.status_code = 400
            response.data = 'invalid otp'
            return response
        user = get_object_or_404(User, phone_number=data['phone_number'])
        serializer = UserResponseSerializer(user)
        return JsonResponse(serializer.data, safe=False)


class UserPage(APIView):
    @swagger_auto_schema(
        operation_summary="получение информации о пользователе",
        responses={200: UserResponseSerializer(), 400: 'ошибочный запрос', 500: "Серверная ошибка"},
        manual_parameters=get_header_params()
    )
    def get(self, request):
        user = User.objects.filter(token=request.headers.get('token'))
        if not user:
            return HttpResponse('Unauthorized', status=401)
        serializer = UserResponseSerializer(user, many=True)
        return JsonResponse(serializer.data, safe=False)
