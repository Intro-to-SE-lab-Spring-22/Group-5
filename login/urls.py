from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
]



urlpatterns += [
    path('login/', views.login_request, name  = 'login')
]

urlpatterns += [
    path("signup/", views.SignUp.as_view(), name = "signup")
]

urlpatterns += [
    path('profile', views.profile, name = "profile")
]

urlpatterns += [
    path('logout', views.logout_request, name = 'logout')
]

urlpatterns += [
    path('deletepost/<int:pk>', views.deletePost, name = 'deletepost')
]

urlpatterns += [
    path('editpost/<int:pk>', views.EditPostView.as_view(), name = 'editpost')
]

urlpatterns += [
    path('addfriend/<int:pk>', views.addFriend, name = 'addfriend')
]