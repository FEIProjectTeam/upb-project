from django.db import models
from django.db.models import CharField, FloatField


class Meal(models.Model):
    name = CharField(max_length=128)
    price = FloatField()

    def __str__(self):
        return self.name
