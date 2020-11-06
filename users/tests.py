from django.test import TestCase
from django.utils import timezone

from users.models import User


class AddUserTest(TestCase):

    def test_add_user(self):
        user = User.objects.create_user('SamPanDonte', 'Bartosz', 'Wawrzyniak', timezone.now(), 'TestPassword')
        self.assertAlmostEqual(User.objects.filter(login='SamPanDonte').first().name, user.name)
        self.assertIsNot(user.password, 'TestPassword')
        self.assertIsInstance(user, User)
