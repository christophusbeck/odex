from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


# Create your models here.

class Users(models.Model):
    username = models.CharField(verbose_name="username", max_length=6, unique=True)
    password = models.CharField(verbose_name="password", max_length=64)
    tan = models.IntegerField(
        verbose_name="TANv",
        validators=[MaxValueValidator(100000), MinValueValidator(1)]
    )


class SecurityAnswers(models.Model):
    username = models.CharField(verbose_name="username", max_length=64)
    answer = models.CharField(verbose_name="username", max_length=64)
    id = models.CharField(
        verbose_name="questionId",
        max_length=10,
        primary_key=True
    )


class SecurityQuestions(models.Model):
    id = models.SmallIntegerField(
        verbose_name="questionId",
        validators=[MaxValueValidator(10), MinValueValidator(1)],
        primary_key=True
    )
    question = models.CharField(verbose_name="username", max_length=128)


class TANs(models.Model):
    authenticated = models.BooleanField(verbose_name="authenticated", default=0)
    tan = models.CharField(verbose_name="TAN", max_length=128)
