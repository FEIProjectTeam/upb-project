from canteen.models import Order, OrderMeal, Meal
from django.contrib.auth.models import User


def get_order_by_id(order_id):
    order = Order.objects.get(id=order_id)
    return order


def get_all_orders_by_user(user: User):
    orders = Order.objects.filter(user=user)
    return orders


def get_unpaid_order_by_user(user: User):
    order = Order.objects.filter(user=user, paid=False).first()
    return order


def create_order(user: User):
    order = Order.objects.create(user=user)
    return order


def add_meal_to_order(user: User, meal: Meal, quantity: int):
    order = get_unpaid_order_by_user(user)
    if order is None:
        order = create_order(user)
    order_meal = OrderMeal.objects.filter(order=order, meal=meal).first()
    if order_meal is None:
        OrderMeal.objects.create(order=order, meal=meal, quantity=quantity)
    else:
        order_meal.quantity = order_meal.quantity + quantity
        order_meal.save()
