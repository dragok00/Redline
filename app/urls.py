from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('foryou/', views.feed, name='feed'),
    path('login/', views.login, name = 'login'),
    path('signup/', views.signup, name = 'signup'),
    path('settings/', views.settings, name = 'settings'),
    path('post/', views.post, name = 'post'),
    path('logout/', views.logout, name = 'logout'),
    path('search/', views.search, name = 'search'),
    path('profile/<str:pk>', views.profile, name = 'profile'),
    path('<str:pk>/', views.detail, name = 'detail'),
    path('<str:pk>/edit/', views.edit, name = 'edit'),
    path('delete-profile', views.delete_profile, name = 'delete-profile'),
    path('<str:pk>/pdf/', views.pdf_preview, name = 'pdf_preview'),
]
