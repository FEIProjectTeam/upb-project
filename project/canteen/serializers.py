from rest_framework.fields import CharField, FloatField
from rest_framework.serializers import Serializer


class MealSerializer(Serializer):
    name = CharField()
    price = FloatField()
