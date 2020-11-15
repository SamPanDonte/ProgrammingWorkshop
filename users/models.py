from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models


class Role(models.Model):
    """Database model for roles"""
    role_name = models.CharField(max_length=30)

    def __str__(self):
        return self.role_name


class User(AbstractBaseUser):
    """Database model for users"""
    login = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=20)
    surname = models.CharField(max_length=30)
    date_of_birth = models.DateField()
    role_id = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    is_deleted = models.BooleanField(default=False)

    objects = BaseUserManager()

    REQUIRED_FIELDS = ['name', 'surname', 'date_of_birth', 'role_id']
    USERNAME_FIELD = 'login'

    def is_super_user(self):
        return self.role_id.role_name == 'admin'
