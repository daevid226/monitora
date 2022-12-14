from rest_framework import serializers

from .models import Actor, Movie


class ActorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Actor
        fields = ["id", "fullName", "url"]


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = "__all__"

    actors = ActorSerializer(many=True, required=True, read_only=False)
