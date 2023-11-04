from django.urls import path

from canteen.views import ListMealsApi, GenerateDummyDatabaseApi, EncryptView

app_name = "canteen"
urlpatterns = [
    path("encrypt/", EncryptView.as_view()),
    path("meals/", ListMealsApi.as_view(), name="list-meals"),
    path(
        "generate/", GenerateDummyDatabaseApi.as_view(), name="generate-dummy-database"
    ),
]
