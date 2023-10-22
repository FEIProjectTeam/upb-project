from canteen.models import Meal


def get_all_meals():
    meals = Meal.objects.all()
    return meals
