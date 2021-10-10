from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import User, Product
from .permissions import HasSellerRolePermission, IsSellerOwnerOfProduct, HasBuyerRolePermission
from .serializer import UserSerializer, ProductSerializer
from .models import CoinChoices


class UserCreateAPIView(GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def user_detail(request, pk=0):
    """
        User Detail API
        Endpoints:
            /user/<id>
        Methods:
            GET, PUT, DELETE, PATCH
    """
    try:
        _user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        user_serializer = UserSerializer(_user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        _data = JSONParser().parse(request)
        user_serializer = UserSerializer(_user, data=_data)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response(user_serializer.data, status=status.HTTP_200_OK)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        _user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
def user_list(request):
    """
        User list API
        Endpoints:
            /users
        Methods:
            GET
    """
    if request.method == 'GET':
        _users = User.objects.all()
        serializer = UserSerializer(_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
def user_create(request):
    """
        User create API
        Endpoints:
            /user
        Methods:
            POST
    """
    if request.method == 'POST':
        user_data = JSONParser().parse(request)
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response(user_serializer.data, status=status.HTTP_201_CREATED)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
@permission_classes([IsAuthenticated, HasSellerRolePermission])
@authentication_classes([TokenAuthentication])
def product_create(request):
    """
        Product create API
        Endpoints:
            /product
        Methods:
            POST
    """
    if request.method == 'POST':
        product_data = JSONParser().parse(request)
        product_data['seller'] = request.user.pk
        product_serializer = ProductSerializer(data=product_data)
        if product_serializer.is_valid():
            product_serializer.save()
            return Response(product_serializer.data, status=status.HTTP_201_CREATED)
        return Response(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
def product_list(request):
    """
        Product list API view
        Endpoints:
            /products
        Methods:
            GET
    """
    if request.method == 'GET':
        _products = Product.objects.all()
        serializer = ProductSerializer(_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsSellerOwnerOfProduct, ])
@authentication_classes([TokenAuthentication])
def product_detail(request, pk):
    """
        Product detail API view
        Endpoints:
            /product/<id>
        Methods:
            GET, PUT, PATCH, DELETE
    """
    try:
        _product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProductSerializer(_product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if not request.user.pk == _product.seller.pk:
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PUT':
        _data = JSONParser().parse(request)
        _data['seller'] = request.user.pk
        serializer = ProductSerializer(_product, data=_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        _product.delete()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, HasBuyerRolePermission])
@authentication_classes([TokenAuthentication])
def deposit(request, amount):
    if amount not in CoinChoices.values:
        return Response({"detail": f"{amount} is an invalid coin"}, status=status.HTTP_406_NOT_ACCEPTABLE)
    _buyer = User.objects.get(pk=request.user.pk)
    _buyer.deposit += amount
    _buyer.save()
    return Response(
        {
            "detail": f"An amount of {amount} is deposited to {_buyer.username}'s account"
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated, HasBuyerRolePermission])
@authentication_classes([TokenAuthentication])
def buy(request):
    product_id = request.query_params.get('product_id', None)
    amount = request.query_params.get('amount', None)
    _message = f"This parameter is required"
    _error_dict = {}

    if product_id is None:
        _error_dict["product_id"] = _message
    else:
        product_id = int(product_id)

    if amount is None:
        _error_dict['amount'] = _message
    elif int(amount) <= 0:
        _error_dict['amount'] = f'{amount} is an invalid amount'
    else:
        amount = int(amount)

    if _error_dict:
        return Response(_error_dict, status=status.HTTP_400_BAD_REQUEST)

    try:
        _product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return Response({"product_id": f'No product matches this query'}, status=status.HTTP_404_NOT_FOUND)

    if _product.amount_available < amount:
        return Response(
            {"detail": f'Only {_product.amount_available} of {_product.product_name} are remaining'},
            status=status.HTTP_400_BAD_REQUEST
        )

    _total_cost = amount * _product.cost
    _user_deposit = request.user.deposit
    if _user_deposit < _total_cost:
        return Response(
            {"detail": f"{request.user.username}'s deposit is less than total cost"},
            status=status.HTTP_400_BAD_REQUEST
        )
    _change = _user_deposit - _total_cost
    request.user.deposit = 0
    request.user.save()
    _product.amount_available -= amount
    _product.save()
    response_dict = {
        "product": _product.product_name,
        "total": _total_cost,
    }
    if _change:  # Normally the machine should return the change whatever it is
        response_dict['change'] = _change

    return Response(response_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, HasBuyerRolePermission])
@authentication_classes([TokenAuthentication])
def reset(request):
    request.user.deposit = 0
    request.user.save()
    return Response(status=status.HTTP_204_NO_CONTENT)
