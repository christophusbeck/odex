from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegistrationView.as_view(), name='register'),
    path('checkusername/', views.CheckUsername.as_view(), name='check_username'),
    path('logout/', views.LogOutView.as_view(), name='logout'),
    # after user clicks logout, he/she should return to login page
    path('user/delete/', views.DeleteAccountView.as_view(), name='delete'),
    path('resetpassword/', views.ResetPasswordView.as_view(), name='reset_password'),
    #path('forgetpassword/', views.ForgetPasswordView.as_view()),
    path('changename/', views.ChangeNameView.as_view(), name='change_name'),
    path('changepassword/', views.ChangePasswordView.as_view(), name='change_password')
    # delete account also like logout, the only difference is that, the count should be deleted(according to suffix nid) and after that get into login page
]
