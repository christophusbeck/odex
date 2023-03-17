import os.path
import shutil

from django.db import models

from odex import settings


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
        help_text="Please enter a valid 3-digit tan number",
        default="None"
    )
    authenticated = models.BooleanField(verbose_name="authenticated", default=0)


class Users(models.Model):
    username = models.CharField(
        verbose_name="username",
        max_length=16,
        help_text="Please enter within 16 letters"
    )
    password = models.CharField(
        verbose_name="password",
        max_length=64,
        help_text="Please enter at least 6 characters"
    )

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        # Delete the directory before the user
        path = '{0}/user_{1}'.format(settings.MEDIA_ROOT, self.id)
        if os.path.exists(path):
            shutil.rmtree(path)

    def __str__(self):
        return self.username + " (id:" + str(self.id) + ")"


class SecurityAnswers(models.Model):
    user = models.OneToOneField(
        to="Users",
        on_delete=models.CASCADE,
        verbose_name="user"
    )
    question = models.ForeignKey(
        to="SecurityQuestions",
        on_delete=models.CASCADE,
        verbose_name="question id",
        default=1
    )
    answer = models.CharField(verbose_name="username", max_length=64)


