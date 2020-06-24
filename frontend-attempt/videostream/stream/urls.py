from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^string/', views.resp_string, name='video'),
    url(r'^stream/', views.livefe, name='stream'),
    url(r'^getframe/', views.receive_image, name='getframe'),
    url(r'^$', views.index, name='index')
]