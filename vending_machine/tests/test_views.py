import json
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status

from vending_machine.models import User, Product
from vending_machine.permissions import *
from vending_machine.utils import (
        create_user, bulk_create_users, authenticate_user, bulk_create_products
    )


class TestUserCreateAPIView(APITestCase):
    """
        Test user create API view
    """

    def setUp(self):
        self.url = reverse('user-create')

    def test_create_user_with_credentials(self):
        sample_user = {
            "username": "Bob",
            "password": "keep-IT_secret"
        }
        response = self.client.post(
            reverse('user-create'),
            data=json.dumps(sample_user),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        sample_user.update({"role": "buyer", "deposit": 0})
        sample_user.pop('password')
        response.data.pop('id')
        self.assertDictEqual(response.data, sample_user)

    def test_create_user_without_username(self):
        sample_user = {"password": "dummy-password"}
        response = self.client.post(
            self.url,
            data=json.dumps(sample_user),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_without_password(self):
        sample_user = {"username": "Foo"}
        response = self.client.post(
            self.url,
            data=json.dumps(sample_user),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_invalid_http_method(self):
        sample_user = {"username": "Bar", "password": "Baz"}
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class TestUserDetailAPIView(APITestCase):
    """
        User detail API view tests
    """

    def setUp(self):
        # Create a user
        self.credentials = {"username": "John", "password": "dummy_password"}
        self.user = create_user(credentials=self.credentials)
        self.url = reverse('user-detail', args=[self.user.id])

    def test_get_user_by_pk(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = self.credentials.copy()
        data.pop('password')
        data.update({"deposit": self.user.deposit, "id": self.user.id, "role": self.user.role})
        self.assertDictEqual(response.data, data)

    def test_user_not_found(self):
        response = self.client.get(reverse('user-detail', args=[0]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_user_invalid_http_method(self):
        response = self.client.post(self.url, data={})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_with_invalid_credentials(self):
        # with invalid deposit and role
        _update_data = {
            "username": "another username",
            "password": "new passwd",
            "deposit": 3,
            "role": "invalid role"
        }
        response = self.client.put(
            self.url, data=json.dumps(_update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['deposit'][0].code, 'invalid_choice')
        self.assertEqual(response.data['role'][0].code, 'invalid_choice')

        # with no password
        _update_data.pop('password')
        response = self.client.put(
            self.url, data=json.dumps(_update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0].code, 'required')

    def test_update_user_with_valid_credentials(self):
        _update_data = {
            "username": "another username",
            "password": "new passwd",
            "deposit": 5,
            "role": "seller"
        }
        response = self.client.put(
            self.url, data=json.dumps(_update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response.data.pop('id')
        _update_data.pop('password')
        self.assertDictEqual(
            response.data,
            _update_data
        )

    def test_delete_existing_user(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Check db for the deleted user
        _user = User.objects.filter(pk=self.user.pk).first()
        self.assertTrue(_user is None)


class TestUserListAPIView(APITestCase):

    def setUp(self):
        self.url = reverse('users-list')
        self.users_list = [
            {"username": "user1", "password": "pass1"},
            {"username": "user2", "password": "pass2"},
            {"username": "user3", "password": "pass3"},
            {"username": "user4", "password": "pass4"},
            {"username": "user5", "password": "pass5"}
         ]
        # Create sample users
        bulk_create_users(users_list=self.users_list)

    def test_get_users_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data), 5)


class TestProductCreateAPIView(APITestCase):
    """
        Product create API view tests
    """

    def setUp(self):
        self.url = reverse('product-create')

    def test_create_product_without_authentication(self):
        response = self.client.post(
            self.url,
            data={"product_name": "test product", "cost": 80},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_product_invalid_auth_credentials(self):
        _user, _ = authenticate_user(username="fake_username", password="fake_pass")
        self.assertEqual(_user, None)
        response = self.client.post(
            self.url,
            data={},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_product_valid_credentials_and_seller_role(self):
        _user = create_user(
            credentials={
                "username": "user1",
                "password": "passwd1",
            },
            role='seller'
        )
        _user, _token = authenticate_user(username="user1", password="passwd1")
        self.assertNotEqual(_user, None)
        # Create product with the created user
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {_token}')
        response = self.client.post(
            self.url,
            data={
                "product_name": "Mac M1",
                "cost": 1500,
                "amount_available": 50,
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_product_as_buyer_user(self):
        _user = create_user(
            credentials={
                "username": "user1",
                "password": "passwd1",
            },
            role="buyer"
        )
        _user, _token = authenticate_user(username="user1", password="passwd1")
        self.assertNotEqual(_user, None)
        # Create product with buyer role
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {_token}")
        response = self.client.post(
            self.url,
            data={
                "product_name": "Test product",
                "cost": 50,
                "amount_available": 10,
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestProductListAPIView(APITestCase):
    """
        Product list API view tests
    """

    def setUp(self):
        self.url = reverse('product-list')
        self.products_list = [
            {"product_name": "prod1", "cost": 5, "amount_available": 10},
            {"product_name": "prod2", "cost": 5, "amount_available": 10},
            {"product_name": "prod3", "cost": 5, "amount_available": 10},
            {"product_name": "prod4", "cost": 5, "amount_available": 10},
            {"product_name": "prod5", "cost": 5, "amount_available": 10},
        ]
        self._user = create_user({"username": "user1", "password": "passwd1"}, role="seller")
        self.products_list = bulk_create_products(self._user, self.products_list)

    def test_product_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json.loads(response.content)), 5)


class TestProductDetailAPIView(APITestCase):
    """
        Product detail API view tests
    """

    def setUp(self):
        self.user = create_user(
            {"username": "user1", "password": "passwd1"},
            role="seller"
        )
        self.product = Product.objects.create(
            product_name="prod1", cost=10, seller=self.user, amount_available=5
        )
        self.url = reverse('product-detail', args=[self.product.pk])

    def test_get_product_not_found(self):
        response = self.client.get(reverse('product-detail', args=[100]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_existing_product(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            response.data,
            {
                "product_name": "prod1", "cost": 10, "seller": self.user.pk,
                "amount_available": 5, "id": self.product.id
            }
        )

    def test_update_product_with_anonymous_user(self):
        response = self.client.put(
            self.url,
            data={
                "product_name": "prod11", "cost": 20, "amount_available": 10
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_product_with_buyer_role(self):
        # Make user with buyer role
        self.user.role = 'buyer'
        self.user.save()

        # Authenticate user and save credentials to request header
        _user, _token = authenticate_user(username=self.user.username, password="passwd1")
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {_token}')

        response = self.client.put(
            self.url,
            data={
                "product_name": "prod11", "cost": 20, "amount_available": 10
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data['detail'],
            SELLER_OWNER_PERMISSION_MESSAGE
        )

    def test_update_product_with_seller_role(self):
        # User with seller role
        self.user.role = 'seller'
        self.user.save()
        # Authenticate user and save auth token to header
        _user, _token = authenticate_user(username=self.user.username, password="passwd1")
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {_token}')

        response = self.client.put(
            self.url,
            data={
                "product_name": "prod11", "cost": 20, "amount_available": 10
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            response.data,
            {
                "product_name": "prod11", "cost": 20, "amount_available": 10,
                "seller": _user.id, "id": self.product.id
            }
        )

    def test_delete_product_buyer_role(self):
        self.user.role = 'buyer'
        self.user.save()
        _, _token = authenticate_user(username=self.user.username, password="passwd1")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {_token}")
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data['detail'],
            SELLER_OWNER_PERMISSION_MESSAGE
        )
        # item shouldn't be deleted
        prod = Product.objects.filter(pk=self.product.pk).first()
        self.assertNotEqual(prod, None)

    def test_delete_product_seller_role(self):
        self.user.role = 'seller'
        self.user.save()
        _, _token = authenticate_user(username=self.user.username, password="passwd1")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {_token}")
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Product item should be deleted
        prod = Product.objects.filter(pk=self.product.pk).first()
        self.assertEqual(prod, None)


class TestProductDepositAPIView(APITestCase):
    """
        /deposit API endpoint tests
    """

    VALID_DEPOSIT = 20
    INVALID_DEPOSIT = 3

    def setUp(self):
        self.buyer_user = create_user(
            {"username": "user1", "password": "passwd1"}, role='buyer'
        )
        self.seller_user = create_user(
            {"username": "user2", "password": "passwd2"}, role='seller'
        )
        self.url = reverse('deposit', args=[self.VALID_DEPOSIT])

    def test_deposit_user_not_authenticated(self):
        response = self.client.get(reverse('deposit', args=[FAKE_USER_ID]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_deposit_user_with_seller_role(self):
        _, _token = authenticate_user(
            username=self.seller_user.username,
            password="passwd2"
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {_token}')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data['detail'],
            BUYER_PERMISSION_MESSAGE
        )

    def test_deposit_user_with_buyer_role(self):
        _initial_deposit = self.buyer_user.deposit
        # Authenticate the buyer user
        _, _token = authenticate_user(
            username=self.buyer_user.username,
            password="passwd1"
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {_token}')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check current deposit is added to user credit
        total_credit = User.objects.get(pk=self.buyer_user.id).deposit
        self.assertEqual(total_credit, _initial_deposit + self.VALID_DEPOSIT)

        # Test with invalid deposit coin
        response = self.client.get(
            reverse('deposit', args=[self.INVALID_DEPOSIT])
        )
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        # Total credit remains unchanged
        self.assertEqual(
            User.objects.get(pk=self.buyer_user.pk).deposit,
            total_credit
        )


class TestProductBuyAPIView(APITestCase):
    """
        /buy API endpoint tests
    """

    def setUp(self):
        self.url = reverse('buy')
        # Create buyer user
        self.buyer = create_user(
            {"username": "user1", "password": "passwd1"}, role='buyer'
        )
        # Create seller user
        self.seller = create_user(
            {"username": "user2", "password": "passwd2"}, role='seller'
        )
        self.product_query = {
            "product_id": 8,
            "amount": 10
        }

    def test_buy_user_not_authenticated(self):
        response = self.client.get(self.url, data=self.product_query)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_buy_user_with_seller_role(self):
        _, _token = authenticate_user(username="user2", password="passwd2")
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {_token}')
        response = self.client.get(self.url, data=self.product_query)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], BUYER_PERMISSION_MESSAGE)

    def test_buy_product_missing_product_id_parameter(self):
        _product = self.product_query.copy()
        _product.pop('product_id')
        _, _token = authenticate_user(username="user1", password="passwd1")
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {_token}')
        response = self.client.get(self.url, data=_product)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['product_id'], "This parameter is required")

    def test_buy_product_missing_amount_parameter(self):
        _product = self.product_query.copy()
        _product.pop('amount')
        _, _token = authenticate_user(username="user1", password="passwd1")
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {_token}')
        response = self.client.get(self.url, data=_product)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['amount'], "This parameter is required")

    def test_buy_product_invalid_amount(self):
        _product = self.product_query.copy()
        _product['amount'] = 0
        _, _token = authenticate_user(username="user1", password="passwd1")
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {_token}')
        response = self.client.get(self.url, data=_product)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['amount'], f"{_product['amount']} is an invalid amount")

    def test_buy_product_not_found(self):
        _, _token = authenticate_user(username="user1", password="passwd1")
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {_token}')
        response = self.client.get(self.url, data=self.product_query)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_buy_product_amount_available_less_than_amount(self):
        _product = Product.objects.create(
            product_name="prod1", amount_available=2, cost=5, seller=self.seller
        )
        _, _token = authenticate_user(username="user1", password="passwd1")
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {_token}')
        response = self.client.get(
            self.url,
            data={"amount": 5, "product_id": _product.id}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['detail'],
            f"Only {_product.amount_available} of {_product.product_name} are remaining"
        )

    def test_buy_product_insufficient_user_credit(self):
        _product = Product.objects.create(
            product_name="prod1", amount_available=2, cost=5, seller=self.seller
        )
        _, _token = authenticate_user(username="user1", password="passwd1")
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {_token}')
        response = self.client.get(
            self.url,
            data={"amount": 1, "product_id": _product.id}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['detail'],
            f"{self.buyer.username}'s deposit is less than total cost"
        )

    def test_buy_product_successful(self):
        _product = Product.objects.create(
            product_name="prod1", amount_available=10, cost=5, seller=self.seller
        )
        _, _token = authenticate_user(username="user1", password="passwd1")
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {_token}')
        self.client.get(reverse('deposit', args=[100]))
        response = self.client.get(
            self.url,
            data={"amount": 2, "product_id": _product.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            response.data,
            {"product": _product.product_name, "total": 2 * 5, "change": 100 - 2 * 5}
        )


class TestProductResetDepositAPIView(APITestCase):
    """
        /reset API endpoint tests
    """

    def setUp(self):
        self.url = reverse('reset')
        self.seller = create_user({"username": "user1", "password": "passwd1"}, role='seller')
        self.buyer = create_user({"username": "user2", "password": "passwd2"}, role='buyer')

    def test_reset_user_not_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reset_user_with_seller_role(self):
        _, _token = authenticate_user(username="user1", password="passwd1")
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {_token}')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reset_user_with_buyer_role(self):
        _, _token = authenticate_user(username="user2", password="passwd2")
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {_token}')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.get(pk=self.buyer.pk).deposit, 0)

