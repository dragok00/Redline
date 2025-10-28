from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('profile/<str:pk>', views.profile, name = 'profile'),
    path('login/', views.login, name = 'login'),
    path('signup/', views.signup, name = 'signup'),
    path('logout/', views.logout, name = 'logout')
]
