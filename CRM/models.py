from django.db import models
from users.models import User


class Industry(models.Model):
    """Database model for industries"""
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Company(models.Model):
    """Database model for companies"""
    name = models.CharField(max_length=30)
    nip = models.CharField(max_length=10, unique=True)
    industry = models.ForeignKey(Industry, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=40)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Note(models.Model):
    """Database model for notes"""
    content = models.TextField()
    is_deleted = models.BooleanField(default=False)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.content


class ContactPerson(models.Model):
    """Database model for contact people"""
    name = models.CharField(max_length=30)
    surname = models.CharField(max_length=40)
    phone = models.CharField(max_length=9)
    mail = models.EmailField()
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name + ' ' + self.surname
