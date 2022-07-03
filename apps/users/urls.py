from django.urls import path

from apps.users.views import RegisterUserView, ActivateCallBackView, LoginView

urlpatterns = [
    path('signup', RegisterUserView.as_view(), name='signup'),
    path('verify_email', ActivateCallBackView.as_view(), name='verify_email'),
    path('login', LoginView.as_view(), name='login'),
]
