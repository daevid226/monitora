from django.shortcuts import render
from django.views import View
from django.views.generic import FormView
from django.views.generic.base import TemplateView
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from .forms import FilterForm

class Login(View):
    template = 'login.html'

    def get(self, request):
        form = AuthenticationForm()
        return render(request, self.template, {'form': form})

    def post(self, request):
        form = AuthenticationForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/index/')
        else:
            return render(request, self.template, {'form': form})

class Index(LoginRequiredMixin, View):
    template = 'index.html'
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def post(self, request):
        content = ""
        form = FilterForm(request.POST)
        if form.is_valid():
            search_text = request.POST.get("search_text")
            
            # vyhledej
            
            
            
            
            content = search_text
        else:
            return self.form_invalid(form) 
    
        return render(request, self.template, {'form': form, "content": content, "title": "Search movies"})
    
    def get(self, request):
        return render(request, self.template, {'form': FilterForm(), "title": "Search movies"})


class MoviesView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    permission_class=[AllowAny]

    def get(self, request, pk):
        ## show actors
        pass
    
        # profile = get_object_or_404(Profile, pk=pk)
        # serializer = ProfileSerializer(profile)
        # return Response({'serializer': serializer, 'profile': profile})

#class Result(View):