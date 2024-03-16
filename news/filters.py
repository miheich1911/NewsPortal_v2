from django_filters import FilterSet, DateFilter, ModelChoiceFilter, CharFilter

from django import forms
from .models import *


class PostFilter(FilterSet):
    title = CharFilter(
        label='Содержит слово',
        lookup_expr='icontains'
    )
    author = ModelChoiceFilter(
        queryset=Author.objects.all(),
        lookup_expr='exact',
        label='Автор',
        empty_label='Любой'
    )
    date_in = DateFilter(
        label='Опубликованы после',
        lookup_expr='gt',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form'})
    )

    class Meta:
        model = Post
        fields = []