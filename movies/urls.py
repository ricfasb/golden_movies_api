from django.urls import path

from movies.views import MoviesView

urlpatterns = [
    path('', MoviesView.as_view(), name='movies')
]
