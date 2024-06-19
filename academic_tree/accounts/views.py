from django.contrib.auth import login as auth_login
from django.shortcuts import render, redirect
from .forms import SignUpForm
from django.contrib.auth.models import User
from mentorship import main
from .models import UserProfile
from django.http import HttpResponse
def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 创建 UserProfile 实例并保存 phone_number
            UserProfile.objects.create(user=user, phone_number=form.cleaned_data['phone_number'])

            main.register(form.cleaned_data['phone_number'],form.cleaned_data['phone_number'], user)

            auth_login(request, user)

            return redirect('mentorship:index')
    else:
        form = SignUpForm()

    return render(request, 'sign_up.html', {'form': form})
def profile(request):
    return redirect('mentorship:index')
def user(request):
    return render(request,'user.html')

