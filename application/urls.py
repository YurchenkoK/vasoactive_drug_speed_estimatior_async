from django.contrib import admin
from django.urls import path
from ssr_inMemory import views

urlpatterns = [
    path('', views.index, name='index'),
    path('vasoactive_drug/<int:drug_id>/', views.vasoactive_drug_detail, name='vasoactive_drug_detail'),
    path('estimation_infusion_speed/', views.estimation_infusion_speed, name='estimation_infusion_speed'),
]