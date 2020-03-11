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
from django.shortcuts import redirect, reverse
from django.contrib.auth import logout
from django.urls import path, include
from django.http import HttpResponse
from urllib.parse import urlencode
from rest_framework import routers
from store import views
from store import api
from revert.views import StopRevertTaskView
from revert.views import RevertTaskView
from revert.views import initiate_revert_view


def logout_view(request):
    logout(request)
    return redirect(reverse('list-batches'))

def robots_view(request):
    return HttpResponse('User-Agent: *\nDisallow: /\n', content_type="text/plain")

def list_tool_batches_redirect(request, tool):
    # for https://github.com/Wikidata/editgroups/issues/32
    return redirect(reverse('list-batches')+'?'+urlencode({'tool': tool}), permanent=True)

urlpatterns = [
    path('api/', include(api)),
    path('', views.BatchesView.as_view(), name='list-batches'),
    path('b/<tool>/', list_tool_batches_redirect, name='list-tool-batches-redirect'),
    path('b/<tool>/<uid>/', views.BatchView.as_view(), name='batch-view'),
    path('b/<tool>/<uid>/edits/', views.BatchEditsView.as_view(), name='batch-edits'),
    path('b/<tool>/<uid>/undo/', initiate_revert_view, name='initiate-revert'),
    path('b/<tool>/<uid>/undo/start/', RevertTaskView.as_view(), name='submit-revert'),
    path('b/<tool>/<uid>/undo/stop/', StopRevertTaskView.as_view(), name='stop-revert'),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('logout/', logout_view, name='logout'),
    path('robots.txt', robots_view, name='robots-txt'),
]
