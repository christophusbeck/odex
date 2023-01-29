from django.db import models


# Create your models here.

class UserInfo(models.Model):
    username = models.CharField(max_length=16, verbose_name="username")
    password = models.CharField(max_length=64, verbose_name="password")
    tan = models.IntegerField(verbose_name="TAN")
    create_time = models.DateTimeField(verbose_name="creating time")

    def __str__(self):
        return self.username
