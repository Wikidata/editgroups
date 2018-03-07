"""editgroups URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from store import views

router = routers.DefaultRouter()
router.register(r'edits', views.EditViewSet)
router.register(r'batches', views.BatchViewSet)
# router.register(r'batches/(?P<id>\d+)/edits/', views.BatchEditsView.as_view(), 'BatchEdits')

urlpatterns = [
    #path('', include(router.urls)),
    path('', views.BatchesView.as_view(), name='list-batches'),
    path('b/<tool>/<uid>/', views.BatchView.as_view(), name='batch-view'),
    path('batches/<int:id>/edits/', views.BatchEditsView.as_view(), name='batch-edits'),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
