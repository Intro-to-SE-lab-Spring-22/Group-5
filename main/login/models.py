from django.db import models
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField
# Create your models here.

class CustomAuthenticationForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={'autofocus': True,'class': 'form-control'}), label_suffix="", max_length= 23)
    password = forms.CharField(
        label=("Password  "),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'form-control' }),
        label_suffix = "",
    )


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class PostManager(models.Manager):
    def likes(self):
        post = Post.objects.get(self)
        return Like.objects.filter(post=post).count() + 1
        
class Post(models.Model):
    content = models.TextField()
    image = models.ImageField(null=True, blank=True, upload_to='images/')
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)

    objects = PostManager()


class Like(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
