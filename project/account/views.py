from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from account.forms import UserRegistrationForm


class UserRegistrationView(View):
    form = UserRegistrationForm()

    def get(self, request, *args, **kwargs):
        return HttpResponse("")

    def post(self, request, *args, **kwargs):
        return HttpResponse("")
