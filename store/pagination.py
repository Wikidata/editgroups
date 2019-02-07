from rest_framework import pagination
from rest_framework.response import Response
from collections import OrderedDict

class PaginationWithoutCounts(pagination.LimitOffsetPagination):
    def paginate_queryset(self, queryset, request, view=None):
        self.limit = self.get_limit(request)
        if self.limit is None:
            return None

        self.offset = self.get_offset(request)
        self.request = request

        results = list(queryset[self.offset:self.offset + self.limit + 1])
        self.more_results_available = len(results) == self.limit + 1
        if self.more_results_available and self.template is not None:
            self.display_page_controls = True

        return results[:self.limit]

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data),
        ]))

    def get_next_link(self):
        if not self.more_results_available:
            return None
        self.count = self.offset + self.limit + 1
        return super(PaginationWithoutCounts, self).get_next_link()

