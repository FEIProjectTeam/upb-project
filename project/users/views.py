from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.views import View

from .forms import RegisterForm

from django_ratelimit.decorators import ratelimit,Ratelimited
from django.utils.decorators import method_decorator

from django.contrib.auth.models import User
from .models import Profile 
from django.http import HttpResponseForbidden

def home(request):
    return render(request, 'users/home.html')

def handler403(request, exception=None):
    if isinstance(exception, Ratelimited):
        return render(request,'users/429.html',status=429)
    return HttpResponseForbidden('Forbidden')

class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'users/register.html'

    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to access the register page while logged in
        if request.user.is_authenticated:
            return redirect(to='/')

        # else process dispatch as it otherwise normally would
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save()  # This saves the User and returns the instance

            # Now create a Profile instance for the new user
            Profile.objects.create(user=user)

            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')
            return redirect(to='login')

        return render(request, self.template_name, {'form': form})

@method_decorator(ratelimit(key='ip', rate='5/m', method='POST'),name='post')
class CustomLoginView(LoginView):
    def form_valid(self, form):
        return super(CustomLoginView, self).form_valid(form)
