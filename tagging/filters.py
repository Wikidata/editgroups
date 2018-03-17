
from rest_framework import filters
from django import forms

class FilteringForm(forms.Form):
    user = forms.CharField(required=False)
    tool = forms.CharField(required=False)
    tags = forms.CharField(required=False)

    def clean_tags(self):
        if not self.cleaned_data.get('tags'):
            return []
        else:
            return self.cleaned_data['tags'].split(',')

class TaggingFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        tags = []
        form = FilteringForm(data=request.GET)
        if not form.is_valid():
            return queryset

        filtered = queryset

        for tag in form.cleaned_data['tags']:
            filtered = filtered.filter(tags__id=tag)
        if form.cleaned_data.get('user'):
            filtered = filtered.filter(user=form.cleaned_data['user'])
        if form.cleaned_data.get('tool'):
            filtered = filtered.filter(tool__shortid=form.cleaned_data['tool'])
        return filtered


def context_processor(request):
    form = FilteringForm(data=request.GET)
    context = {}
    if form.is_valid():
        context['tagging_form'] = form.cleaned_data
    return context


