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
from .models import CustomAuthenticationForm, CustomUserCreationForm, Post, ThreadModel, MessageModel
from .forms import PostForm, CommentForm, ThreadForm, MessageForm
from django.views.generic import UpdateView
from django.db.models import Q
from django.views import View

# Create your views here.



def home(request):
    if request.user.is_authenticated:
        friends = Friend.objects.friends(request.user)
        friends.append(request.user)
        ordered_posts = Post.objects.order_by('-created_at')
        posts = list(ordered_posts.filter(user__in = friends))
        friends = Friend.objects.friends(request.user)
    else:
        posts = []
        friends = []
    context = {
        'posts': posts,
        'friends': friends,
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
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            return redirect('profile')
    else:
        form = PostForm()
    friends = Friend.objects.friends(request.user)
    posts = list(reversed(Post.objects.filter(user = request.user)))
    username = request.POST.get('username_search',False)
    search = list(User.objects.filter(username = username))
    friendRequests = Friend.objects.unread_requests(request.user)

    context = {
        'posts': posts,
        'form': form,
        'search': search,
        'friends': friends,
        'friendrequests': friendRequests,
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

def addComment(request, pk):
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.post = Post.objects.get(pk=pk)
            instance.user = request.user
            instance.save()
            return redirect('/')
    else:
        form = CommentForm()

    context = {
        'form': form,
    }

    return render(request, 'addcomment.html', context = context)

def likePostHome(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.likes.add(request.user)
    return redirect('/')

def likePostProfile(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.likes.add(request.user)
    return redirect('profile')

class EditPostView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = "editpost.html"

    def get_object(self, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        # We can also get user object us\ng self.request.user  but that doesnt work
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
            messages.info(request, "You already sent a request to " + other_user.username)
            return(redirect("profile"))
    if Friend.objects.are_friends(request.user, other_user) == False:
        Friend.objects.add_friend(
            request.user,
            other_user
        )
        messages.info(request, "Sent friend request")
        return redirect('profile')
    else:
        messages.info(request, "You are already friends!")
        return(redirect("profile"))

    return render(request, 'addfriend.html')

def acceptFriend(request, pk):
    friend_request = FriendshipRequest.objects.get(pk=pk)
    friend_request.accept()
    messages.info(request, "Accepted friend request")
    return redirect('profile')

class ListThreads(View):
    def get(self, request, *args, **kwargs):
        threads = ThreadModel.objects.filter(Q(user=request.user) | Q(receiver=request.user))

        context = {
            'threads':threads
        }

        return render(request, 'inbox.html', context=context)

class CreateThread(View):
    def get(self, request, *args, **kwargs):
        form = ThreadForm()

        context = {
            'form': form
        }

        return render(request, 'create_thread.html', context=context)

    def post(self, request, *args, **kwargs):
        form = ThreadForm(request.POST)

        username = request.POST.get('username')

        try:
            receiver = User.objects.get(username=username)
            if ThreadModel.objects.filter(user=request.user, receiver=receiver).exists():
                thread = ThreadModel.objects.filter(user=request.user, receiver=receiver)[0]
                return redirect('thread', pk=thread.pk)
            elif ThreadModel.objects.filter(user=receiver, receiver=request.user).exists():
                thread = ThreadModel.objects.filter(user=receiver, receiver=request.user)[0]
                return redirect('thread', pk=thread.pk)

            if form.is_valid():
                thread = ThreadModel(
                    user=request.user,
                    receiver=receiver
                )
                thread.save()

                return redirect('thread', pk=thread.pk)
        except:
            messages.info(request, "This user is not your friend")
            return redirect('create-thread')

class ThreadView(View):
    def get(self, request, pk, *args, **kwargs):
        form = MessageForm()
        thread = ThreadModel.objects.get(pk=pk)
        message_list = MessageModel.objects.filter(thread__pk__contains=pk)
        context = {
            'thread': thread,
            'form': form,
            'message_list': message_list
        }

        return render(request, 'thread.html', context)

class CreateMessage(View):
    def post(self, request, pk, *args, **kwargs):
        thread = ThreadModel.objects.get(pk=pk)
        if thread.receiver == request.user:
            receiver = thread.user
        else:
            receiver = thread.receiver

        message = MessageModel(
            thread=thread,
            sender_user=request.user,
            receiver_user=receiver,
            body=request.POST.get('message')
        )

        message.save()
        return redirect('thread', pk=pk)
