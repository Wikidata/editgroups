
from store import views

from django.urls import path

urlpatterns = [
    path('b/<tool>/<uid>/', views.APIBatchView.as_view(), name='api-batch-view'),
    path('', views.APIBatchesView.as_view(), name='api-list-batches'),
    path('b/<tool>/<uid>/edits/', views.APIBatchEditsView.as_view(), name='api-batch-edits'),
]

