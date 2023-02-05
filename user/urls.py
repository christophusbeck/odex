from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.LoginView.as_view()),
    path('register/', views.RegistrationView.as_view()),
    path('checkusername/', views.CheckUsername.as_view(), name='check_username'),
    path('logout/', views.LogOutView.as_view()),
    # after user clicks logout, he/she should return to login page
    path('delete/', views.DeleteAccountView.as_view()),
    # delete account also like logout, the only difference is that, the count should be deleted(according to suffix nid) and after that get into login page
]
