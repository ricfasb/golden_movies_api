from rest_framework import serializers

from movies.models import Movie


class MovieSerializer(serializers.ModelSerializer):
    studios = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )
    producers = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = Movie
        fields = ['id', 'year', 'title', 'studios', 'producers', 'winner']