from django.contrib import admin
from django.urls import path
from ssr_inDb import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('vasoactive_drug/<int:drug_id>/', views.vasoactive_drug_detail, name='vasoactive_drug_detail'),
    path('add_to_order/<int:drug_id>/', views.add_to_order, name='add_to_order'),
    path('estimation_infusion_speed/', views.estimation_infusion_speed, name='estimation_infusion_speed'),
    path('delete_order/<int:order_id>/', views.delete_order, name='delete_order'),
]