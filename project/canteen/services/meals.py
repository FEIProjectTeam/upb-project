from canteen.models import Meal


def get_all_meals():
    meals = Meal.objects.all()
    meals_data = [
        {"id": meal.id, "name": meal.name, "price": meal.price} for meal in meals
    ]
    return meals_data


def get_meal_by_id(meal_id):
    meal = Meal.objects.filter(id=meal_id).first()
    return meal
