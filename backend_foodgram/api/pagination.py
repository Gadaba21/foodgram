from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import JSONRenderer

from .constants import MAX_PAGE_SIZE, PAGE_SIZE


class CustomPageNumberPagination(PageNumberPagination):
    page_size = PAGE_SIZE
    page_size_query_param = 'limit'
    max_page_size = MAX_PAGE_SIZE


class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if 'results' in data:
            results = data.pop('results')
            data = results
        return super().render(data, accepted_media_type, renderer_context)