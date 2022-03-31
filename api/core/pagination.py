from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    '''
    https://www.django-rest-framework.org/api-guide/pagination/
    '''
    page_size = 10
    # page_size_query_param = 'page_size'
    # max_page_size = 1000

    def get_paginated_response(self, data):
        return Response({
            'total_records': self.page.paginator.count,
            'page_size': self.get_page_size(request=self.request),
            'page': self.get_page_number(request=self.request, paginator=self.page.paginator),
            'results': data
        })
