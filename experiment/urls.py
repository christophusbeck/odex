from django.urls import path

import user.views
from . import views

urlpatterns = [
    path('main/', views.MainView.as_view()),
    path('delete/', views.DeleteView.as_view()),
    path('configuration/', views.Configuration.as_view()),
    path('aboutus/', user.views.AboutUsView.as_view()),
    path('login/', user.views.LoginView.as_view()),
    path('result/', views.ResultView.as_view()),
    path('explist/', views.ExperimentListView.as_view(), name='explist'),
]
