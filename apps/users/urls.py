from django.urls import path

from apps.users.views import RegisterUserView

urlpatterns = [
    path('signup', RegisterUserView.as_view(), name='signup'),
]
