from django.urls import path
from . import views


urlpatterns = {
    path('login/', views.LoginView.as_view()),
    path('signup/', views.RegistrationView.as_view()),
}
