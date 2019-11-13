from django.conf.urls import url
from django.contrib import admin

from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$', 'upload', name='upload'),
    # url(r'^$', TemplateView.as_view(template_name='upload.html'), name='index'),
]