from django.contrib.auth.models import User
from django.db import models
from django.db.models import CharField, FloatField


class Meal(models.Model):
    name = CharField(max_length=128, unique=True)
    price = FloatField()

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meals = models.ManyToManyField(Meal, through="OrderMeal")
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(editable=False, auto_now_add=True)

    def __str__(self):
        return f"Order[id:{self.id}, user:{self.user.username}, paid:{self.paid}]"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    stars = models.PositiveIntegerField()
    comment = CharField(max_length=128)


class OrderMeal(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
