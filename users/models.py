from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models


class Role(models.Model):
    """Database model for roles"""
    role_name = models.CharField(max_length=30)


class UserManager(BaseUserManager):
    """Class for managing users"""
    def create_user(self, login, name, surname, date_of_birth, password, role=None):  # TODO role
        """Create and save user to database"""
        user = self.model(
            name=name,
            surname=surname,
            date_of_birth=date_of_birth,
            login=login,
            role_id=role
        )
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser):
    """Database model for users"""
    name = models.CharField(max_length=20)
    surname = models.CharField(max_length=30)
    date_of_birth = models.DateField()
    login = models.CharField(max_length=30, unique=True)
    role_id = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    is_deleted = models.BooleanField(default=False)

    objects = UserManager()

    REQUIRED_FIELDS = ['name', 'surname', 'date_of_birth', 'role_id']
    USERNAME_FIELD = 'login'

    def is_super_user(self):
        return self.role_id is None
