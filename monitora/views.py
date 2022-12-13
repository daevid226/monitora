from api import views as api_views
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic import FormView
from django.views.generic.base import TemplateView
from rest_framework.permissions import AllowAny
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView

from .forms import FilterForm


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

            content = search_text
        else:
            return self.form_invalid(form)

        return render(request, self.template, {"form": form, "content": content, "title": "Search movies"})

    def get(self, request):
        return render(request, self.template, {"form": FilterForm(), "title": "Search movies"})


class MoviesView(APIView):
    template = "detail.html"
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request, pk):
        response = api_views.MovieViewSet.get_movie_detail(request, pk)
        movie = response.data
        return render(request, self.template, {"movie": movie})
