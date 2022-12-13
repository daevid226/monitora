from django.contrib.auth.models import Group, User
from django.forms.models import model_to_dict  # noqa
from rest_framework import serializers

from .models import Actor, Movie


class ActorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Actor
        fields = ["url", "givenName", "lastName"]


class MovieSerializer(serializers.ModelSerializer):
    queryset = Movie.objects.all().order_by("title")
    actors = ActorSerializer(many=True)

    # no need
    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     response['category'] = model_to_dict(Category.objects.get(pk=instance.category.id))
    #     response['contractor'] = model_to_dict(Contractor.objects.get(pk=instance.contractor.id))
    #     response['solver'] = model_to_dict(Solver.objects.get(pk=instance.solver.id))
    #     return response
