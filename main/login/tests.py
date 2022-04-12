from django.test import TestCase
from login.models import Post, User, Comment
# Create your tests here.

class CommentsTestCase(TestCase):
    def setUp(self):
        User.objects.create(username='user')
        Comment.objects.create(post=Post.objects.create(content="hi"))

    def testUserPosts(self):
        comment = Comment.objects.get(Post.objects.get(content='hi'))
        comment.post.check()

class PostAndLikeTestCase(TestCase):
    def setUp(self):
        User.objects.create(username='user')
        Post.objects.create(content="hi")

    def testUserPosts(self):
        me = Post.objects.get(content='hi')
        me.likes.add(User.objects.get(username='user'))

class CreateAccountTestCase(TestCase):
    def setUp(self):
        User.objects.create(username='user', password="password", email='email@email.com')

    def testUserCreation(self):
        me = User.objects.get(username='user')
        me.check()

class LoginAccountTestCase(TestCase):
    def setUp(self):
        User.objects.create(username='user', password="password")

    def testUserLogin(self):
        me = User.objects.get(username='user')
        raw_password='password'
        me.check_password(self)
        if me.is_authenticated:
            return True