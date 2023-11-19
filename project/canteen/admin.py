from django.contrib import admin

from canteen.models import Meal, Order, OrderMeal

admin.site.register(Meal)
admin.site.register(Order)
admin.site.register(OrderMeal)
