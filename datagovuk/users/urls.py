from django.contrib.auth import views as auth_views
from django.urls import path

from datagovuk.users import views

app_name = "users"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
