from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from .models import Profile

@login_required(login_url = 'login')
def index(request):
    user_object = User.objects.get(username = request.user.username)
    user_profile = Profile.objects.get(user = user_object)
    
    context = {
        'user_object': user_object,
        'user_profile': user_profile
    }
    return render(request, 'index.html', context)

@login_required(login_url = 'login')
def profile(request, pk):
    user_object = User.objects.get(username = pk)
    user_profile = Profile.objects.get(user = user_object)
    
    context = {
        'user_object': user_object,
        'user_profile': user_profile
    }
    return render(request, 'profile.html', context)

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        
        if password == password2 and len(password) > 7:
            if User.objects.filter(email = email).exists():
                messages.info(request, "Email taken")
                return redirect('signup')
            elif User.objects.filter(username = username).exists():
                messages.info(request, 'Username taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username = username, email = email, password = password)
                user.save()
                
                user_login = auth.authenticate(username = username, password = password)
                auth.login(request, user_login)
                
                user_object = User.objects.get(username = username)
                user_profile = Profile.objects.create(user = user_object, id_user = user_object.id)
                user_profile.save()

                return redirect('profile', pk = user_object)
        else:
            messages.info(request, 'Password does not match')
            return redirect('signup')
    
    else:
        return render(request, 'signup.html')
    
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = auth.authenticate(username = username, password = password)
        
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        
        else:
            messages.info(request, 'Invalid credentials')
            return redirect('login')
    
    else:
        return render(request, 'login.html')
    
@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    return redirect('login')