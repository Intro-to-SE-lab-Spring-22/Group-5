from django.contrib import admin
from .models import User
# Register your models here.
#admin.site.register(User)
from login.models import Post, Comment

admin.site.register(Post)
admin.site.register(Comment)