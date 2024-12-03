from rest_framework.test import APITestCase
from rest_framework import status


class APIIntegrationTests(APITestCase):

    def test_get_movies(self):
        response = self.client.get('/movies/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_top_studios(self):
        response = self.client.get('/movies/?projection=studios-with-win-count')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_winners_by_year(self):
        response = self.client.get('/movies/?year=2023&winner=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_producer_intervals(self):
        response = self.client.get('/movies/?projection=max-min-win-interval-for-producers')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_years_with_multiple_winners(self):
        response = self.client.get('/movies/?projection=years-with-multiple-winners')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_route(self):
        response = self.client.get('/invalid')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
