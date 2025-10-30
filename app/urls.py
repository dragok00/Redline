from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('profile/<str:pk>', views.profile, name = 'profile'),
    path('login/', views.login, name = 'login'),
    path('signup/', views.signup, name = 'signup'),
    path('settings/', views.settings, name = 'settings'),
    path('post/', views.post, name = "post"),
    path('submit_location/', views.submit_location, name = 'submit_location'),
    path('logout/', views.logout, name = 'logout')
]
