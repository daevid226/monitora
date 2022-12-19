from django.forms.models import model_to_dict
from rest_framework import serializers

from .models import Actor, Movie


class ActorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Actor
        fields = ["id", "fullName", "url"]


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ["id", "url", "title", "actors"]

    actors = serializers.PrimaryKeyRelatedField(many=True, required=True, queryset=Actor.objects.all())

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["actors"] = [model_to_dict(Actor.objects.get(pk=actor_id)) for actor_id in response["actors"]]
        return response
