from django.db import models


# Create your models here.

class SecurityQuestions(models.Model):
    question = models.CharField(
        verbose_name="question",
        max_length=1024,
        help_text="please select a security question"
    )


class TANs(models.Model):
    tan = models.CharField(
        verbose_name="TAN",
        max_length=6,
        help_text="Please enter 3 characters",
        default="None"
    )
    authenticated = models.BooleanField(verbose_name="authenticated", default=0)


class Users(models.Model):
    username = models.CharField(
        verbose_name="username",
        max_length=6,
        help_text="Please enter within 6 letters"
    )
    password = models.CharField(
        verbose_name="password",
        max_length=64,
        help_text="Please enter at least 6 characters"
    )


class SecurityAnswers(models.Model):
    user = models.OneToOneField(
        to="Users",
        on_delete=models.CASCADE,
        verbose_name="user"
    )
    question_id = models.OneToOneField(
        to="SecurityQuestions",
        on_delete=models.CASCADE,
        verbose_name="question id",
        default=1
    )
    answer = models.CharField(verbose_name="username", max_length=64)


