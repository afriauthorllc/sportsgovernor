from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('matches/', views.match_list, name='match_list'),
    path('create-slip/', views.create_slip, name='create_slip'),
    path('slip/<int:slip_id>/', views.slip_detail, name='slip_detail'),
]

