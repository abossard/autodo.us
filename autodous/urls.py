"""
Definition of urls for autodo.us.
"""

from datetime import datetime
from django.conf.urls import patterns, url

# Uncomment the next lines to enable the admin:
from django.conf.urls import include
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from graphene.contrib.django.views import GraphQLView
from autodous_base.schema import schema
admin.autodiscover()

urlpatterns = [  # Examples:
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^graphql/', csrf_exempt(GraphQLView.as_view(schema=schema))),
    url(r'^graphiql/', include('django_graphiql.urls')),
    url(r'^todos/', include('todos.urls')),
    url(r'^', include('autodous_base.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
]
