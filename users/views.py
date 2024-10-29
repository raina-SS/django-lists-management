from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.views.decorators.csrf import requires_csrf_token

from .forms import RegistrationForm

@requires_csrf_token
def index(request):
    reg_form = RegistrationForm()
    login_form = AuthenticationForm()
    if request.method == 'POST':
        if 'register' in request.POST:
            reg_form = RegistrationForm(request.POST)
            if reg_form.is_valid():
                user = reg_form.save()
                login(request, user)
                messages.success(request, 'Registration successful.')
                return redirect('/lists')
            else:
                messages.error(request, "Registration failed. Please check the information.")
        elif 'login' in request.POST:
            login_form = AuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, "Login successful.")
                    return redirect('/lists')
                else:
                    messages.error(request, "Invalid username or password.")
            else:
                messages.error(request, "Login failed. Please check your credentials.")
    context = {'reg_form': reg_form, 'login_form': login_form, 'title': 'Home'}
    return render(request, 'users/index.html', context)

def logout_user(request):
    logout(request)
    messages.success(request, 'Logged out user.')
    return redirect('/')