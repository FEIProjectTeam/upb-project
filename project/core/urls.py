"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin

from canteen.views import (
    ListMealsApi,
    EncryptView,
    GenerateDummyDatabaseApi,
    UploadPubKeyView,
    encrypt_page,
    genRSAKeysView,
    DecryptPriKeyView,
)

from django.urls import path, include, re_path

from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth import views as auth_views
from users.views import CustomLoginView,handler403


from users.forms import LoginForm

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/meals/", ListMealsApi.as_view()),
    path("api/generate/", GenerateDummyDatabaseApi.as_view()),
    path("encrypt/", EncryptView.as_view()),
    path('comun/', encrypt_page, name='encrypt-page'),  
    path(
        "encrypt/pub-key/", UploadPubKeyView.as_view(), name="encryption-upload-pub-key"
    ),
    path(
        "decrypt/pri-key/", DecryptPriKeyView.as_view(), name="encryption-decrypt-pri-key"
    ),
    path(
        "encrypt/gen-rsa-keys/",
        genRSAKeysView,
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
    
handler403 = 'users.views.handler403'