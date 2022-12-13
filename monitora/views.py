from django.shortcuts import render
from django.views import View
from django.views.generic import FormView
from django.views.generic.base import TemplateView
from django.http import HttpResponse, HttpResponseNotFound

from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView

from .forms import FilterForm


class MoviesView(APIView):
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request, pk):
        pass
    
        # profile = get_object_or_404(Profile, pk=pk)
        # serializer = ProfileSerializer(profile)
        # return Response({'serializer': serializer, 'profile': profile})


class Index(View):
    template = 'index.html'

    def get(self, request):
        if request.method == "POST":
            form = FilterForm(request.POST)
            if form.is_valid():
                print("HLEADMMM")
                return HttpResponse('Yay valid')
        else:
            form = FilterForm()
        
        return render(request, self.template, {'form': form, "title": "Search text"})


#class Result(View):