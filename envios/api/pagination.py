# envios/api/pagination.py
"""
Clases de paginación personalizadas para la API.

Uso desde la URL:
  /api/encomiendas/?page=2              ← PageNumber
  /api/encomiendas/?page=2&page_size=5  ← tamaño variable
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class EncomiendaPagination(PageNumberPagination):
    """
    Paginación estándar para listas de encomiendas.

    Respuesta incluye metadatos de paginación:
      {
        "count": 50,
        "total_pages": 5,
        "next": "http://.../api/encomiendas/?page=3",
        "previous": "http://.../api/encomiendas/?page=1",
        "results": [...]
      }
    """
    page_size             = 10          # Por defecto 10 por página
    max_page_size         = 100         # Máximo permitido
    page_size_query_param = 'page_size' # Permite ?page_size=5 desde la URL

    def get_paginated_response(self, data):
        return Response({
            'count'      : self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'next'       : self.get_next_link(),
            'previous'   : self.get_previous_link(),
            'results'    : data,
        })

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'count'      : {'type': 'integer'},
                'total_pages': {'type': 'integer'},
                'next'       : {'type': 'string', 'nullable': True},
                'previous'   : {'type': 'string', 'nullable': True},
                'results'    : schema,
            },
        }
