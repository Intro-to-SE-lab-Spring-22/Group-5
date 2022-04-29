from django import forms
from django.forms import Textarea
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, Comment


# Create your forms here.
class PostForm(forms.ModelForm):
    class Meta:
        model = Post

        fields = (
            'content',
            'image',
        )

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment

        fields = (
            'content',
        )

class ThreadForm(forms.Form):
    username = forms.CharField(label='', max_length=100)

class MessageForm(forms.Form):
    message = forms.CharField(label='', max_length=1000)
