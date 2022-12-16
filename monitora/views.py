import requests
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import FormView

from .forms import FilterForm


class Login(FormView):
    template_name = "login.html"
    form_class = AuthenticationForm
    success_url = "/index/"

    def post(self, request):
        form = AuthenticationForm(request.POST)
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect("/index/")
        else:
            return render(request, self.template_name, {"form": form})


class Index(LoginRequiredMixin, FormView):
    login_url = "/login/"
    redirect_field_name = "redirect_to"
    #
    title = "Search movies and actors"
    template_name = "index.html"
    form_class = FilterForm
    success_url = "/index/"

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        if isinstance(request, TemplateResponse):
            return request

        form = FilterForm(request.POST)
        if not form.is_valid():
            return self.form_invalid(form)

        search_text = request.POST.get("search_text")

        url = request.build_absolute_uri(reverse("api-search", args={search_text}))

        response = requests.get(url, params=request.POST)
        response.raise_for_status()

        results = response.json()["results"]  # return movies & actors

        return render(
            request,
            self.template_name,
            {"form": form, "movies": results["movies"], "actors": results["actors"], "title": self.title, **results},
        )


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
