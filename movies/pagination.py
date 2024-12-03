from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'pageSize'

    def get_paginated_response(self, data):
        sorted_param = self.request.query_params.get('sort', None)
        is_sorted = sorted_param is not None

        return Response({
            'content': data,
            'pageable': {
                'sort': {
                    'sorted': is_sorted,
                    'unsorted': not is_sorted
                },
                'pageSize': self.page.paginator.per_page,
                'pageNumber': self.page.number - 1,
                'offset': (self.page.number - 1) * self.page.paginator.per_page,
                'paged': True,
                'unpaged': False
            },
            'totalElements': self.page.paginator.count,
            'last': not self.page.has_next(),
            'totalPages': self.page.paginator.num_pages,
            'first': not self.page.has_previous(),
            'sort': {
                'sorted': is_sorted,
                'unsorted': not is_sorted
            },
            'number': self.page.number - 1,
            'numberOfElements': len(data),
            'size': self.page.paginator.per_page
        })
