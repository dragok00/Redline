from django.db import models
from django.contrib.auth import get_user_model
import shortuuidfield
User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name = 'profile')
    id_user = models.IntegerField()
    bio = models.TextField(blank = True)
    profile_image = models.ImageField(upload_to = 'profile_images/', default = "default-profile-pic.jpeg", blank = True)

    def __str__(self):
        return self.user.username

class Post(models.Model):
    id = shortuuidfield.ShortUUIDField(primary_key = True, max_length = 22)
    username = models.ForeignKey(Profile, on_delete = models.CASCADE)
    caption = models.TextField(blank = True)
    make = models.CharField(max_length = 30, blank = True)
    model = models.CharField(max_length = 80, blank = True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    image = models.ImageField(upload_to = 'staticwebsiteimg/', blank = False)
    created_at = models.DateTimeField(auto_now_add = True)

    likes = models.ManyToManyField(User, related_name = 'liked_posts', blank = True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.username.user.username
    
    def total_likes(self):
        return self.likes.count()
    

class UserRelationships(models.Model):
    user_from = models.ForeignKey(User, related_name = 'rel_from_set', on_delete = models.CASCADE)
    user_to = models.ForeignKey(User, related_name = 'rel_to_set', on_delete = models.CASCADE)
    created = models.DateTimeField(auto_now_add = True, db_index = True)

    class Meta:
        ordering = ['-created']
        constraints = [
            models.UniqueConstraint(fields = ['user_from', 'user_to'], name = 'unique_rel'),
        ]

    def __str__(self):
        return '{} follows {}'.format(self.user_from, self.user_to)
    
User.add_to_class('following', models.ManyToManyField('self', through = UserRelationships, related_name = 'followers', symmetrical = False))