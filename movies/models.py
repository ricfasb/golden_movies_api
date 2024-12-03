from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver


class Studio(models.Model):
    objects = None
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Producer(models.Model):
    objects = None
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Movie(models.Model):
    objects = None
    title = models.CharField(max_length=255)
    year = models.PositiveIntegerField()
    studios = models.ManyToManyField(Studio)
    producers = models.ManyToManyField(Producer)
    winner = models.BooleanField(default=False)

    def __str__(self):
        return self.title


@receiver(post_migrate)
def load_movies(sender, **kwargs):
    from django.core.management import call_command
    call_command('load_movies')