from django_filters import rest_framework as filters

from .models import Title


class TitlesFilter(filters.FilterSet):
    category = filters.CharFilter(field_name='category__slug')
    genre = filters.CharFilter(field_name='genre__slug')
    name = filters.CharFilter(field_name='name', lookup_expr='contains')

    class Meta:
        fields = ('name', 'category', 'genre', 'year')
        model = Title
     
