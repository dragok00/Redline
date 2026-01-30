from django.contrib import admin
from .models import Profile, Post

class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'caption', 'make', 'model', 'latitude', 'longitude', 'image', 'created_at']

admin.site.register(Profile)
admin.site.register(Post, PostAdmin)