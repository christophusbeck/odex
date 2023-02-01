from django.db import models

# Create your models here.
class Experiments(models.Model):
    userid = models.IntegerField(verbose_name="user id")
    experiment_name = models.CharField(verbose_name="experiment name")