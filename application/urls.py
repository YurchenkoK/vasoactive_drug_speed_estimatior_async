from django.contrib import admin
from django.urls import path, include
from stocks import views
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ===== HTML ИНТЕРФЕЙС (веб-сайт) =====
    path('', views.search, name='search'),
    path('vasoactive_drug/<int:drug_id>/', views.vasoactive_drug_detail, name='vasoactive_drug_detail'),
    path('add_to_order/<int:drug_id>/', views.add_to_order_html, name='add_to_order'),
    path('estimation_infusion_speed/', views.estimation_infusion_speed, name='estimation_infusion_speed'),
    path('estimation_infusion_speed/<int:order_id>/', views.estimation_infusion_speed, name='estimation_infusion_speed_with_id'),
    path('update_order_params/<int:order_id>/', views.update_order_params, name='update_order_params'),
    path('complete_order/<int:order_id>/', views.complete_order_html, name='complete_order'),
    path('delete_order/<int:order_id>/', views.delete_order_html, name='delete_order'),
    
    # ===== REST API (для Postman/Insomnia) =====
    path('api/', include(router.urls)),
    
    # API endpoints для препаратов (Drug)
    path('api/drugs/', views.DrugList.as_view(), name='drug-list'),
    path('api/drugs/<int:pk>/', views.DrugDetail.as_view(), name='drug-detail'),
    path('api/drugs/<int:pk>/add-image/', views.add_drug_image, name='drug-add-image'),
    path('api/drugs/<int:pk>/add-to-order/', views.add_drug_to_order, name='drug-add-to-order'),
    
    # API endpoints для заявок (Order)
    path('api/orders/cart/', views.cart_icon, name='cart-icon'),
    path('api/orders/', views.OrderList.as_view(), name='order-list'),
    path('api/orders/<int:pk>/', views.OrderDetail.as_view(), name='order-detail'),
    path('api/orders/<int:pk>/form/', views.form_order, name='order-form'),
    path('api/orders/<int:pk>/complete/', views.complete_order, name='order-complete'),
    path('api/orders/<int:pk>/reject/', views.reject_order, name='order-reject'),
    
    # API endpoints для препаратов в заявке (м-м)
    path('api/orders/<int:order_pk>/drugs/<int:drug_pk>/', views.remove_drug_from_order, name='drug-in-order-delete'),
    path('api/orders/<int:order_pk>/drugs/<int:drug_pk>/update/', views.update_drug_in_order, name='drug-in-order-update'),
    
    # API endpoints для пользователей
    path('api/users/', views.UsersList.as_view(), name='users-list'),
    path('api/users/register/', views.UserRegistration.as_view(), name='user-register'),
    
    # DRF auth
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
