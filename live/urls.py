from django.urls import path
from . import views
urlpatterns = [
    path('', views.live_list, name='live_list'),
    path('standings/', views.standings_list, name='standings_list'),
]