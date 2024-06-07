from django.contrib.auth import login as auth_login
from django.shortcuts import render, redirect
from accounts.forms import SignUpForm


def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('mentorship:node_detail')
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})

