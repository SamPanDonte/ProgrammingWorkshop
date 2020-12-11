from django.test import TestCase
from django.utils import timezone

from users.models import User


class AddUserTest(TestCase):

    def test_add_user(self):
        user = User()
        user.name = 'Bartek'
        user.surname = 'Wawrzyniak'
        user.login = 'SamPanDonte'
        user.date_of_birth = '2000-05-15'
        user.save()
        self.assertAlmostEqual(User.objects.get(login='SamPanDonte').name, user.name)
        self.assertIsNot(user.password, 'TestPassword')
        self.assertIsInstance(user, User)
