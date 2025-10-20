from django.contrib import admin
from django.urls import path
from stocks import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.search, name='search'),
    path('vasoactive_drug/<int:drug_id>/', views.vasoactive_drug_detail, name='vasoactive_drug_detail'),
    path('add_to_order/<int:drug_id>/', views.add_to_order, name='add_to_order'),
    path('estimation_infusion_speed/', views.estimation_infusion_speed, name='estimation_infusion_speed'),
    path('estimation_infusion_speed/<int:order_id>/', views.estimation_infusion_speed, name='estimation_infusion_speed_with_id'),
    path('update_order_params/<int:order_id>/', views.update_order_params, name='update_order_params'),
    path('complete_order/<int:order_id>/', views.complete_order, name='complete_order'),
    path('delete_order/<int:order_id>/', views.delete_order, name='delete_order'),
]