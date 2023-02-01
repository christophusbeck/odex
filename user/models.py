from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


# Create your models here.

class Users(models.Model):
    username = models.CharField(
        verbose_name="username",
        max_length=6,
        unique=True,
        help_text="Please enter within 6 letters"
    )
    password = models.CharField(
        verbose_name="password",
        max_length=64,
        help_text="Please enter at least 6 characters"
    )
    tan = models.IntegerField(
        verbose_name="TAN",
        validators=[MaxValueValidator(100000), MinValueValidator(1)],
        help_text="Please enter at least 6 characters"
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
