from django.urls import path

from . import views

urlpatterns = [
    path('main/', views.MainView.as_view(), name='main'),
    path('delete/', views.DeleteView.as_view(), name='delete_exp'),
    path('configuration/', views.Configuration.as_view(), name='configuration'),
    path('result/', views.ResultView.as_view(), name='result'),
    path('explist/', views.ExperimentListView.as_view(), name='explist'),
]
