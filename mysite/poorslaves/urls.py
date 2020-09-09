from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    path('random', views.random, name='random'),
    path('accept', views.accept_answer, name='accept'),
    path('show_answers', views.show_answers, name='show_answers'),
    path('show_answers_excel', views.show_answers_excel, name='show_answers_excel'),
    path('logout', views.my_logout, name='logout'),
    path('accept-reject', views.accept_reject, name='accept-reject'),
    path('open-console-wDeOYXpoRcqXUnY09dBy', views.open_console, name='open_console'),
    path('console', views.admin_console, name='console')
              ]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)