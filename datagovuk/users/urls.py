from django.urls import path

from datagovuk.users import views

app_name = "users"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
]
