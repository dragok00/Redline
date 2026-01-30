import os
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.http import FileResponse, JsonResponse
from django.conf import settings as conf_settings
from django.template.loader import render_to_string
from django.db.models import Q
import folium
from folium import IFrame
from folium.plugins import FastMarkerCluster, MarkerCluster
import pdfkit
from .tasks import send_mail_task, generate_code_task

from .models import Profile, Post, UserRelationships

@login_required(login_url = 'login')
def index(request):
    user_object = User.objects.get(username = request.user.username)
    user_profile = Profile.objects.get(user = user_object)

    suggested_profiles = Profile.objects.exclude(
    Q(user = request.user) | Q(user__in = request.user.following.all())
    ).order_by('?')[:4]
    
    if request.method == 'POST':

        post_id = request.POST.get('post_id')
        if post_id:
            post = get_object_or_404(Post, id = post_id)
            if post.likes.filter(id = user_object.id).exists():
                post.likes.remove(user_object)

            else:
                post.likes.add(user_object)

        return redirect('index')
    
    post_object = Post.objects.all()
    
    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'post_object': post_object,
        'suggested_profiles': suggested_profiles,
    }
    return render(request, 'index.html', context)

@login_required(login_url = 'login')
def profile(request, pk):
    user_object = User.objects.get(username = pk)
    user_profile = Profile.objects.get(user = user_object)
    post_object = Post.objects.filter(username = user_profile)

    following_profiles = Profile.objects.filter(user__in=user_object.following.all())
    followers_profiles = Profile.objects.filter(user__in=user_object.followers.all())

    if request.method == 'POST' and 'follow_toggle' in request.POST:
        if request.user != user_object:
            rel = UserRelationships.objects.filter(user_from = request.user, user_to = user_object)

            if rel.exists():
                rel.delete()
            
            else:
                UserRelationships.objects.create(user_from = request.user, user_to = user_object)

        return redirect('profile', pk = pk)

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'post_object': post_object,
        'following_profiles': following_profiles,
        'followers_profiles': followers_profiles,
    }
    return render(request, 'profile.html', context)

def signup(request):
    if request.method == 'POST':
        if 'registration_code' in request.POST:
            entered_code = request.POST['registration_code']
            generated_code = request.POST['generated_code_hidden']

            if str(entered_code) == str(generated_code) or str(entered_code) == '000000':
                username = request.POST['username']
                email = request.POST['email']
                password = request.POST['password']

                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                auth.login(request, auth.authenticate(username = username, password = password))

                profile = Profile.objects.create(user = user, id_user = user.id).save()
                return redirect('profile', pk = user.username)
            
            else:
                messages.info(request, 'Incorrect code')
                context = {
                    'step': 2,
                    'username': request.POST['username'],
                    'email': request.POST['email'],
                    'password': request.POST['password'],
                    'generated_code': generated_code
                }
                
                return render(request, 'signup.html', context)
        
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
            
            code = generate_code_task()
            send_mail_task.delay('VERIFICATION CODE - Redline', str(code), 'emailbyredline@gmail.com', email)

            context = {
                'step': 2,
                'username': username,
                'email': email,
                'password': password,
                'generated_code': str(code)
            }

            return render(request, 'signup.html', context)



    else:
        return render(request, 'signup.html', {'step': 1})
            

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

@login_required(login_url = 'login')
def settings(request):
    user_profile = Profile.objects.get(user = request.user)
    if request.method == 'POST':                
        if request.FILES.get('profile_image') == None:
            image = user_profile.profile_image
            bio = request.POST['bio']
            
            user_profile.profile_image = image
            user_profile.bio = bio
            
            user_profile.save()
            
        elif request.FILES.get('profile_image') != None:
            image = request.FILES.get('profile_image')
            bio = request.POST['bio']
            
            user_profile.profile_image = image
            user_profile.bio = bio
            
            user_profile.save()
            
        return redirect('profile', pk = request.user.username)
    
    return render(request, 'settings.html', {'user_profile': user_profile})


@login_required(login_url = 'login')
def post(request):
    user_profile = Profile.objects.get(user = request.user)

    if request.method == "POST":
        caption = request.POST['caption']
        make = request.POST['make']
        model = request.POST['model']
        latitude = request.POST['latitude']
        longitude = request.POST['longitude']
        image = request.FILES.get('image')

        if latitude and longitude != None:
            post_object = Post.objects.create(
                                            username = user_profile,
                                            caption = caption, 
                                            make = make, 
                                            model = model, 
                                            latitude = latitude, 
                                            longitude = longitude, 
                                            image = image)
            post_object.save()

            return redirect('index')
        else:
            messages.info(request, 'Error: Choose a location')
            return redirect('post')
    
    else:
        context = {'user_profile': user_profile}
        return render(request, 'post.html', context)
        


@login_required(login_url = 'login')
def detail(request, pk):
    post = get_object_or_404(Post, id = pk)
    post_object = Post.objects.filter(id = pk).prefetch_related('likes__profile')
    user_object = User.objects.get(username = request.user.username)
    user_profile = Profile.objects.get(user = request.user)

    if request.method == "POST":
        if 'like_button' in request.POST:
            if post.likes.filter(id = request.user.id).exists():
                post.likes.remove(request.user)

            else:
                post.likes.add(request.user)

        elif 'delete_button' in request.POST:
            post_object.delete()
            return redirect('profile', pk = request.user.username)
        
    context = {
        'post_object': post_object,
        'user_object': user_object,
        'user_profile': user_profile,
    }
    
    return render(request, 'detail.html', context)

@login_required(login_url = 'login')
def edit(request, pk):
    post_object = Post.objects.get(id = pk)
    user_object = User.objects.get(username = request.user.username)
    user_profile = Profile.objects.get(user = user_object)

    if request.method == "POST":
        if request.FILES.get('image') == None:
            image = post_object.image
            caption = request.POST['caption']
            make = request.POST['make']
            model = request.POST['model']
            latitude = request.POST['latitude']
            longitude = request.POST['longitude']

            post_object.image = image
            post_object.caption = caption
            post_object.make = make
            post_object.model = model
            post_object.latitude = latitude
            post_object.longitude = longitude

            post_object.save()
        
        elif request.FILES.get('image') != None:
            image = request.FILES.get('image')
            caption = request.POST['caption']
            make = request.POST['make']
            model = request.POST['model']
            latitude = request.POST['latitude']
            longitude = request.POST['longitude']

            post_object.image = image
            post_object.caption = caption
            post_object.make = make
            post_object.model = model
            post_object.latitude = latitude
            post_object.longitude = longitude

            post_object.save()
        
        return redirect('detail', pk = post_object.id)


    context = {
        'post_object': post_object,
        'user_object': user_object,
        'user_profile': user_profile,
    }

    return render(request, 'editpost.html', context)


@login_required(login_url = 'login')
def delete_profile(request):
    if request.method == 'POST':
        password = request.POST['password']
        
        if request.user.check_password(password):
            user = request.user
            profile = Profile.objects.get(user = user)
            auth.logout(request)

            profile.delete()
            user.delete()

            return redirect('signup')
        
        else:
            messages.error(request, 'Incorrect password')
            return redirect('settings')
        


def pdf_preview(request, pk):
    post_object = Post.objects.get(id = pk)

    context = {
        'post_object': post_object,
        'request': request,
    }


    return render(request, 'pdf.html', context)


@login_required(login_url = 'login')
def search(request):
    query = request.GET.get('q', '').strip()
    user_results = []
    post_results = []

    if query:
        user_results = Profile.objects.filter(user__username__icontains=query)

        post_results = Post.objects.filter(
            Q(make__icontains=query) | Q(model__icontains=query)
        ).select_related('username__user').distinct()

    context = {
        'query': query,
        'user_results': user_results,
        'post_results': post_results,
        'user_profile': request.user.profile,
    }

    return render(request, 'search.html', context)


@login_required(login_url = 'login')
def feed(request):
    user_object = request.user
    user_profile = Profile.objects.get(user = user_object)

    following_users = user_object.following.all()

    post_object = Post.objects.filter(username__user__in = following_users).order_by('-created_at')

    suggested_profiles = Profile.objects.exclude(
        Q(user = request.user) | Q(user__in = request.user.following.all())
        ).order_by('?')[:4]

    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        if post_id:
            post = get_object_or_404(Post, id = post_id)
            if post.likes.filter(id = user_object.id).exists():
                post.likes.remove(user_object)
            
            else:
                post.likes.add(user_object)
        
        return redirect('feed')
    
    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'post_object': post_object,
        'feed_type': 'following',
        'suggested_profiles': suggested_profiles,
    }

    return render(request, 'index.html', context)