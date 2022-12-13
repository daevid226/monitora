import requests
from api import views as api_views
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic.base import TemplateView

from .forms import FilterForm

# from rest_framework.renderers import TemplateHTMLRenderer


class Login(View):
    template = "login.html"

    def get(self, request):
        form = AuthenticationForm()
        return render(request, self.template, {"form": form})

    def post(self, request):
        form = AuthenticationForm(request.POST)
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect("/index/")
        else:
            return render(request, self.template, {"form": form})


class Index(LoginRequiredMixin, View):
    template = "index.html"
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def post(self, request):
        content = ""
        form = FilterForm(request.POST)
        if form.is_valid():
            search_text = request.POST.get("search_text")

            # vyhledej

            # to rest api filter

            content = search_text
        else:
            return self.form_invalid(form)

        return render(request, self.template, {"form": form, "content": content, "title": "Search movies"})

    def get(self, request):
        return render(request, self.template, {"form": FilterForm(), "title": "Search movies"})


class MovieDetail(LoginRequiredMixin, View):
    template = "detail/movie.html"
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request, movie_id):
        url = request.build_absolute_uri(f"/api/movies/{movie_id}")
        response = requests.get(url, params=request.GET)
        movie = response.json()
        return render(request, self.template, {"movie": movie})


class ActorDetail(LoginRequiredMixin, View):
    template = "detail/actor.html"
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request, actor_id):
        url = request.build_absolute_uri(f"/api/actors/{actor_id}")
        response = requests.get(url, params=request.GET)
        actor = response.json()
        return render(request, self.template, {"actor": actor})
