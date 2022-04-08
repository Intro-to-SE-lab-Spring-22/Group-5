from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.shortcuts import  render, redirect
from django.contrib.auth import login, authenticate #add this
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm #add this
from django.contrib.auth.models import User
from friendship.models import Friend, Follow, Block, FriendshipRequest
from .models import CustomAuthenticationForm, CustomUserCreationForm, Post
from .forms import PostForm
from django.views.generic import UpdateView
# Create your views here.



def home(request):
    num_users = User.objects.all().count()
    list_users = []
    for x in User.objects.all():
        if x.get_username() != request.user.get_username():
            list_users.append(x.get_username())
    context = {
        'num_users': num_users,
        'list_users': list_users,
    }
    return render(request, 'home.html', context = context)

def login_request(request):
	if request.method == "POST":
		form = CustomAuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}.")
				return redirect("profile")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	if request.method != 'POST': form = CustomAuthenticationForm()
	return render(request=request, template_name="login.html", context={"login_form":form})

def logout_request(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('home')

def profile(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            return redirect('profile')
    else:
        form = PostForm()

    posts = list(reversed(Post.objects.filter(user = request.user)))
    username = request.POST.get('username_search',False)
    search = list(User.objects.filter(username = username))

    context = {
        'posts': posts,
        'form': form,
        'search': search,
    }
    return render(request, 'profile.html', context = context)

def deletePost(request, pk):
    post = Post.objects.get(pk=pk)
    post.delete()
    return redirect('profile')

def editPost(request, pk):
    form = EditPostForm(request.POST, pk)
    context = {
        'form': form
    }
    return render(request, 'editpost.html', context = context)

class EditPostView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = "editpost.html"

    def get_object(self, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])

        # We can also get user object using self.request.user  but that doesnt work
        # for other models.

        return post

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy("profile")

class SignUp(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'register.html'

def addFriend(request, pk):
    other_user = User.objects.get(pk=pk)
    list = Friend.objects.sent_requests(user=request.user)
    for friend in list:
        if friend.to_user==other_user:
            return(redirect("profile"))
    if Friend.objects.are_friends(request.user, other_user) == False:
        Friend.objects.add_friend(
            request.user,
            other_user
        )
    else:
        messages.info(request, "You are already friends!")
        return(redirect("profile"))

    return render(request, 'addfriend.html')
