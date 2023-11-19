from collections import defaultdict

from django.db.models import Sum, F, Max, Count

from canteen.models import Order, OrderMeal, Meal
from django.contrib.auth.models import User


def get_unpaid_order_by_id_and_user(order_id: int, user: User):
    order = Order.objects.filter(id=order_id, user=user, paid=False).first()
    return order

def get_paid_order_by_id_and_user(order_id: int, user: User):
    order = Order.objects.filter(id=order_id, user=user, paid=True).first()
    return order

def get_all_orders_by_user(user: User):
    orders = Order.objects.filter(user=user)
    return orders


def get_unpaid_order_data_for_user(user: User):
    data = (
        OrderMeal.objects.filter(
            order__user=user,
            order__paid=False,
        )
        .values(
            "order_id",
            "meal__name",
            "meal__price",
            "quantity",
        )
        .annotate(
            meal_total_price=F("meal__price") * F("quantity"),
        )
        .distinct()
    )
    if not data.exists():
        return None
    total_price = data.aggregate(total_price=Sum("meal_total_price"))["total_price"]
    return {"data": list(data), "total_price": total_price}


def get_paid_order_data_for_user(user: User):
    data = (
        OrderMeal.objects.filter(
            order__user=user,
            order__paid=True,
        )
        .values(
            "order_id",
            "meal__name",
            "meal__price",
            "quantity",
        )
        .annotate(
            meal_total_price=F("meal__price") * F("quantity"),
        )
        .distinct()
        .order_by("-order__created_at")
    )
    if not data.exists():
        return None
    structured_data = defaultdict(lambda: {"data": [], "total_price": 0})
    for row in data:
        order_id = row["order_id"]
        structured_data[order_id]["data"].append(row)
        structured_data[order_id]["total_price"] += row["meal_total_price"]
    structured_data.default_factory = None
    return structured_data


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


def pay_for_order(order: Order):
    order.paid = True
    order.save()
