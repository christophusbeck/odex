from django.db import models


# Create your models here.

class User(models.Model):
    username = models.CharField(verbose_name="user_name", max_length=64)
    password = models.CharField(verbose_name="password", max_length=64)

class SecurityAnswer(models.Model):
    username = models.CharField(verbose_name="user_name", max_length=64)
    answer = models.CharField(verbose_name="user_name", max_length=64)
    id = models.CharField(verbose_name="questionId", max_length=10)

class SecurityQuestion(models.Model):
    id = models.SmallIntegerField(verbose_name="questionId", max_length=10)
    question = models.CharField(verbose_name="user_name", max_length=128)


class TAN(models.Model):
    authenticated = models.BooleanField(verbose_name="authenticated", default=0)
    code = models.CharField(verbose_name="TAN", max_length=128)
