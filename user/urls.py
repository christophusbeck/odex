from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.LoginView.as_view()),
    path('register/', views.RegistrationView.as_view()),
    path('logout/', views.LogOutView.as_view()),
    path('aboutus/', views.AboutUsView.as_view()),
    path('user/<int:nid>/delete/', views.DeleteAccountView.as_view()),
    path('test/', views.Test.as_view()),
]
