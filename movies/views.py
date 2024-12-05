from collections import defaultdict

from django.db.models import Count, Q
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from movies.models import Studio, Movie
from movies.pagination import CustomPagination
from movies.serializers import MovieSerializer


class MoviesView(APIView, PageNumberPagination):
    """
    API View para possibilitar a leitura da lista de indicados e vencedores
    da categoria Pior Filme do Golden Raspberry Awards

    Attributes:
        size (str): parametro com a quantidade de items por pagina.
        page (str): parametro indicando o numero da pagina.
    """
    page_size_query_param = 'size'
    page_query_param = 'page'

    def get(self, request):
        projection = request.query_params.get('projection', '')

        if 'years-with-multiple-winners' in projection:
            return self.years_with_multiple_winners(request)
        elif 'studios-with-win-count' in projection:
            return self.studios_with_win_count(request)
        elif projection == 'max-min-win-interval-for-producers':
            return self.producer_intervals(request)
        else:
            return self.movies(request)

    def movies(self, request):
        queryset = Movie.objects.all()
        sort_param = request.query_params.get('sort', 'id')
        year_filter = request.query_params.get('year', None)
        winner_filter = request.query_params.get('winner', None)

        if year_filter:
            queryset = queryset.filter(year=year_filter)

        if winner_filter is not None:
            if winner_filter.lower() == 'true':
                queryset = queryset.filter(winner=True)
            elif winner_filter.lower() == 'false':
                queryset = queryset.filter(winner=False)

        queryset = queryset.order_by(sort_param)

        page = request.query_params.get('page', None)
        size = request.query_params.get('size', None)

        if page is None and size is None:
            if year_filter is None or winner_filter is None:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            serializer = MovieSerializer(queryset, many=True)
            return Response(serializer.data)

        paginator = CustomPagination()
        results = paginator.paginate_queryset(queryset, request, view=self)
        serializer = MovieSerializer(results, many=True)

        sorted_param = request.query_params.get('sort', None)
        is_sorted = sorted_param is not None

        return paginator.get_paginated_response(serializer.data)

    def years_with_multiple_winners(self, request):
        """
            Query com anos que tiveram mais de um vencedor
        """
        years = (Movie.objects.filter(winner=True)
                 .values('year')
                 .annotate(winner_count=Count('year'))
                 .filter(winner_count__gt=1)
                 .order_by('year'))

        data = [
            {
                'year': entry['year'],
                'winnerCount': entry['winner_count']
            }
            for entry in years
        ]
        return Response({'years': data})

    def studios_with_win_count(self, request):
        """
            Query contendo os três estúdios com mais vitórias
        """
        studios = (Studio.objects.annotate(
            winCount=Count('movie', filter=Q(movie__winner=True)))
                   .filter(winCount__gt=0)
                   .order_by('-winCount')[:3])

        data = [
            {
                'name': studio.name,
                'winCount': studio.winCount
            }
            for studio in studios
        ]
        return Response({'studios': data})

    def producer_intervals(self, request):
        """
            Query com produtores com maior e menor intervalo entre vitórias
        """
        winners = (Movie.objects.filter(winner=True)
                   .prefetch_related('producers')
                   .order_by('year'))

        producer_years = defaultdict(list)

        # Adicionamos todos os produtores no dicionario
        for winner in winners:
            for producer in winner.producers.all():
                # quebramos os produtores em conjuncao
                if 'and' in str(producer):
                    producers = str(producer).split('and')
                    for producer_joined in producers:
                        producer_years[producer_joined.strip()].append(winner.year)
                    continue
                producer_years[str(producer)].append(winner.year)

        # Filtramos os que tenham vencido mais de uma vez
        filtered_producer_years = {producer: years for producer, years in producer_years.items() if len(years) > 1}

        producer_max_interval = self.get_producers_max_interval(filtered_producer_years)
        max_interval = 1 if len(producer_max_interval) == 0 else producer_max_interval[0]['interval']
        producer_min_interval = self.get_producers_min_interval(max_interval, filtered_producer_years)

        return Response({
            'min': producer_min_interval,
            'max': producer_max_interval
        })

    def get_producers_max_interval(self, filtered_producer_years):
        producer_max_interval = []
        max_interval = 0

        # Percorre os anos por produtor
        for producer, years in filtered_producer_years.items():
            # rimeiramente ordenamos
            ordered_years = sorted(years)

            for i in range(1, len(ordered_years)):
                interval = ordered_years[i] - ordered_years[i - 1]

                if interval > max_interval:
                    producer_max_interval.clear()
                    max_interval = interval
                    producer_max_interval.append({
                        'producer': str(producer),
                        'interval': interval,
                        'previousWin': ordered_years[i - 1],
                        'followingWin': ordered_years[i]
                    })
                elif interval == max_interval:
                    producer_max_interval.append({
                        'producer': str(producer),
                        'interval': interval,
                        'previousWin': ordered_years[i - 1],
                        'followingWin': ordered_years[i]
                    })

        return producer_max_interval

    def get_producers_min_interval(self, max_interval, filtered_producer_years):
        producer_min_interval = []
        min_interval = max_interval

        # Percorre os anos por produtor
        for producer, years in filtered_producer_years.items():
            # rimeiramente ordenamos
            ordered_years = sorted(years)

            for i in range(1, len(ordered_years)):
                interval = ordered_years[i] - ordered_years[i - 1]

                if interval < min_interval:
                    min_interval = interval
                    producer_min_interval.clear()
                    producer_min_interval.append({
                        'producer': str(producer),
                        'interval': interval,
                        'previousWin': ordered_years[i - 1],
                        'followingWin': ordered_years[i]
                    })
                elif interval == min_interval:
                    producer_min_interval.append({
                        'producer': str(producer),
                        'interval': interval,
                        'previousWin': ordered_years[i - 1],
                        'followingWin': ordered_years[i]
                    })

        return producer_min_interval
