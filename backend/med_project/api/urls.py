from django.urls import path

from .views import login_view, save_profile_view


urlpatterns = [
    path("login/", login_view, name="login"),
    path("profile/save/", save_profile_view, name="save_profile"),
]
