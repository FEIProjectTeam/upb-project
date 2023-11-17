from django.db import models
from django.db.models import CharField, FloatField


class Meal(models.Model):
    name = CharField(max_length=128, unique=True)
    price = FloatField()

    def __str__(self):
        return self.name


class Order(models.Model):
    meal = models.ForeignKey('Meal', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    special_requests = models.TextField(blank=True)
    paid = models.BooleanField(default=False)
