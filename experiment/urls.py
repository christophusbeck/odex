from django.urls import path

import user.views
from . import views


urlpatterns = [
    path('main/', views.MainView.as_view()),
    path('configuration/', views.Configuration.as_view()),
    path('login/',user.views.LoginView.as_view()),
    path('finishedDetail/',views.FinishedDetailView.as_view()),
    path('pendingDetail/', views.PendingDeatilView.as_view()),
]
