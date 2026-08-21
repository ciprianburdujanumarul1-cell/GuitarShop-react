
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signin/", views.s, name="signin"),
    path("login/", views.l, name="login"),
    path("logout/", views.logout_view, name="logout"), 
    
]

