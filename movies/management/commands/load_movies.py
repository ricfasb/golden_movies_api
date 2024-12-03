import csv

from django.core.management import BaseCommand

from movies.models import Movie, Studio, Producer


class Command(BaseCommand):
    help = 'Load movies from CSV'

    def handle(self, *args, **kwargs):
        with open('movies/data/movielist.csv', 'r') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                # Primeiramente criamos o filme
                movie, _ = Movie.objects.get_or_create(
                    year=row['year'],
                    title=row['title'],
                    winner=(row['winner'].strip().lower() == 'yes')
                )

                # Adicionamos os studios ao filme
                studios_field = row['studios']
                if studios_field:
                    studio_names = [s.strip() for s in studios_field.split(',')]
                    for studio_name in studio_names:
                        studio, _ = Studio.objects.get_or_create(name=studio_name)
                        movie.studios.add(studio)

                # Adicionamos os produtores ao filme
                producers_field = row['producers']
                if producers_field:
                    producer_names = [p.strip() for p in producers_field.split(',')]
                    for producer_name in producer_names:
                        producer, _ = Producer.objects.get_or_create(name=producer_name)
                        movie.producers.add(producer)
