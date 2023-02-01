from django.shortcuts import render, redirect
from django.views import View

from experiment.forms import CreateForm


# Create your views here.

class MainView(View):
    template_name = "main.html"  # waiting for html file

    def get(self, request, *args, **kwargs):
        form = CreateForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = CreateForm()
        if form.is_valid():
            form.save()
            return redirect('/main/')
        return render(request, self.template_name, {"form": form})