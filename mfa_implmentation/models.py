from django.db import models
from django.contrib.auth.models import User


class UserInformation(models.Model):
    username = models.ForeignKey(User, on_delete=models.SET_NULL,null=True, related_name="user")
    accountNumber = models.CharField(max_length=11)
    favourite_dish = models.CharField(max_length=200)
    middle_name = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
