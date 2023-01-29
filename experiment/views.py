from django.shortcuts import render, redirect
from django.views import View


# Create your views here.

class MainView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'main.html')

    def post(self, request, *args, **kwargs):
        pass