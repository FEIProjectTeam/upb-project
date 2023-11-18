from canteen.models import Order
from django.contrib.auth.models import User

def get_order_by_id(order_id):
    order = Order.objects.get(id=order_id)
    return order


def get_all_orders():
    orders = Order.objects.all()
    return orders


def create_order(meal, quantity, paid=False):
    order = Order.objects.create(meal=meal, quantity=quantity, paid=paid)
    return order
