from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.summary),
    url(r'^summary/', views.summary, name='summary'),
    url(r'^detail/(?P<pk>\d+)$', views.detail, name='detail'),
]
