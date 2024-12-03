from django.db.models import Count, Q, Min, Max, F
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
        pageSize (str): parametro com a quantidade de items por pagina.
        page (str): parametro indicando o numero da pagina.
    """
    page_size_query_param = 'pageSize'
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
        return Response(data)

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
        return Response(data)

    def producer_intervals(self, request):
        """
            Query com produtores com maior e menor intervalo entre vitórias
        """
        winners = (Movie.objects.filter(winner=True).values('producers__name')
            .annotate(
                count_wins=Count('id'),
                first_year=Min("year"),
                last_year=Max("year"),
                interval=F("last_year") - F("first_year")
            )
            .filter(count_wins__gt=1)
            .filter(interval__gt=0)
        )

        intervals = winners.aggregate(
            min_interval=Min('interval'),
            max_interval=Max('interval')
        )

        min_interval = intervals['min_interval']
        max_interval = intervals['max_interval']

        producer_max_intervals = winners.filter(interval=max_interval) if max_interval > 0 else None
        producer_min_intervals = winners.filter(interval=min_interval) if min_interval > 0 else None

        min_producers = []
        max_producers = []

        if producer_max_intervals:
            for producer_max_interval in producer_max_intervals:
                max_producers.append({
                    'producer': producer_max_interval['producers__name'],
                    'interval': producer_max_interval['interval'],
                    'previousYear': producer_max_interval['first_year'],
                    'followingYear': producer_max_interval['last_year']
                })

        if producer_min_intervals:
            for producer_min_interval in producer_min_intervals:
                min_producers.append({
                    'producer': producer_min_interval['producers__name'],
                    'interval': producer_min_interval['interval'],
                    'previousYear': producer_min_interval['first_year'],
                    'followingYear': producer_min_interval['last_year']
                })

        return Response({
            'min': min_producers,
            'max': max_producers
        })
