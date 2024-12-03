from django.apps import AppConfig
from django.contrib import admin

from movies.models import Movie, Studio, Producer


@admin.register(Movie)
class CarAdmin(admin.ModelAdmin):
    pass


@admin.register(Studio)
class StudioAdmin(admin.ModelAdmin):
    pass


@admin.register(Producer)
class ProducerAdmin(admin.ModelAdmin):
    pass
