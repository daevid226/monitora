from django.db import models
from psqlextra.indexes import UniqueIndex


class Actor(models.Model):
    givenName = models.TextField(null=False, max_length=80)
    lastName = models.TextField(null=False, default='', max_length=80)
    fullName = models.TextField(unique=True, null=False, max_length=256)
    url = models.TextField(null=False, max_length=1024)
    
    class Meta:
        ordering = ['lastName']
        indexes = [
            UniqueIndex(fields=["fullName"]),
        ]

    def __str__(self):
        return self.fullName


class Movie(models.Model):
    title = models.TextField(unique=True, null=False, max_length=256)
    url = models.TextField(null=False, max_length=1024)
    actors = models.ManyToManyField(Actor, through="MovieActor")

    class Meta:
        ordering = ['title']
        indexes = [
            UniqueIndex(fields=["title"]),
        ]
        
    def __str__(self):
        return self.title


class MovieActor(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)

    def __str__(self):
        return "{}_{}".format(self.movie.__str__(), self.acotor.__str__())