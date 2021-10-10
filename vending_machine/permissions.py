from rest_framework.permissions import BasePermission

from vending_machine.models import Product

BUYER_PERMISSION_MESSAGE = 'The user must be a buyer'
SELLER_PERMISSION_MESSAGE = 'The user is not a seller'
SELLER_OWNER_PERMISSION_MESSAGE = 'The user must be a seller, and owns the product'

FAKE_USER_ID = 1000


class HasSellerRolePermission(BasePermission):
    message = SELLER_PERMISSION_MESSAGE

    def has_permission(self, request, view):
        if request.user.role == 'seller':
            return True
        return False

    def has_object_permission(self, request, view, obj):
        return True


class IsSellerOwnerOfProduct(BasePermission):
    message = SELLER_OWNER_PERMISSION_MESSAGE

    def has_permission(self, request, view):
        if request.method in ('PUT', 'PATCH', 'DELETE'):
            pk = view.kwargs.get('pk', None)
            product = Product.objects.get(pk=pk)
            if request.user.pk == product.seller.pk and request.user.role == 'seller':
                return True
        elif request.method == 'GET':
            return True

        return False


class HasBuyerRolePermission(BasePermission):
    message = BUYER_PERMISSION_MESSAGE

    def has_permission(self, request, view):
        return request.user.role == 'buyer'
