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
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    answer = models.CharField(verbose_name="username", max_length=64)
    id = models.CharField(
        verbose_name="questionId",
        max_length=10,
        primary_key=True
    )


class SecurityQuestions(models.Model):
    question = models.CharField(verbose_name="question", max_length=1024)


class TANs(models.Model):
    authenticated = models.BooleanField(verbose_name="authenticated", default=0)
    tan = models.CharField(verbose_name="TAN", max_length=128)
