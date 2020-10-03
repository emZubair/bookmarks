from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from account.forms import LoginForm


# Create your views here.
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            username = form_data['username']
            password = form_data['password']
            import pdb;
            pdb.set_trace()
            user = authenticate(request, username=username,
                                password=password)
            message = 'Invalid Login'
            if user is not None:
                if user.is_active:
                    login(request, user)
                    message = 'Authenticated Successfully'
                else:
                    message = 'User is not active'

            return HttpResponse(message)
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})
