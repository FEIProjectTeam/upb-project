from django.contrib import admin

from canteen.models import Meal, Order, OrderMeal, Review

admin.site.register(Meal)
admin.site.register(Order)
admin.site.register(OrderMeal)
admin.site.register(Review)
