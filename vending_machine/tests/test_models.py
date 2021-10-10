from rest_framework.test import APITestCase
from vending_machine.models import User


class TestModel(APITestCase):
    """
        User model tests
    """

    def setUp(self):
        pass

    def test_create_user(self):
        user = User.objects.create_user('test', 'testpass')
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, 'test')
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_staff)

    def test_create_super_user(self):
        user = User.objects.create_superuser('test', 'testpass')
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, 'test')
        self.assertTrue(user.is_admin)
        self.assertTrue(user.is_staff)

    def test_raise_error_when_no_username(self):
        self.assertRaises(ValueError, User.objects.create_user, username=None, password='')

    def test_raise_error_when_no_password(self):
        self.assertRaises(ValueError, User.objects.create_user, username='user1', password=None)
