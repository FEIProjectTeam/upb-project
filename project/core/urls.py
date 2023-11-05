from django.contrib import admin

from canteen.views import (
    ListMealsApi,
    EncryptView,
    GenerateDummyDatabaseApi,
    UploadPubKeyView,
    encrypt_page,
    GenRSAKeysView,
    DecryptPriKeyView,
)

from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth import views as auth_views
from users.views import CustomLoginView


from users.forms import LoginForm

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/meals/", ListMealsApi.as_view()),
    path("api/generate/", GenerateDummyDatabaseApi.as_view()),
    path("encrypt/", EncryptView.as_view()),
    path("comun/", encrypt_page, name="encrypt-page"),
    path(
        "encrypt/pub-key/", UploadPubKeyView.as_view(), name="encryption-upload-pub-key"
    ),
    path(
        "decrypt/pri-key/",
        DecryptPriKeyView.as_view(),
        name="encryption-decrypt-pri-key",
    ),
    path(
        "encrypt/gen-rsa-keys/",
        GenRSAKeysView.as_view(),
        name="encryption-gen-rsa-keys",
    ),
    path("users/", include("users.urls")),
    path("", include("users.urls")),
    path(
        "login/",
        CustomLoginView.as_view(
            redirect_authenticated_user=True,
            template_name="users/login.html",
            authentication_form=LoginForm,
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(template_name="users/logout.html"),
        name="logout",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = "users.views.handler403"
