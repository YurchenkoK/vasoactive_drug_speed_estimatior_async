from django.contrib import admin
from django.urls import path, include
from stocks import views
from rest_framework import routers, permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

router = routers.DefaultRouter()

schema_view = get_schema_view(
   openapi.Info(
      title="Vasoactive Drugs API",
      default_version='v1',
      description="API для системы управления вазоактивными препаратами и заявками",
      contact=openapi.Contact(email="contact@vasoactive.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # HTML views (не включаются в Swagger)
    path('', views.search, name='search'),
    path('vasoactive_drug/<int:drug_id>/', views.vasoactive_drug_detail, name='vasoactive_drug_detail'),
    path('add_to_order/<int:drug_id>/', views.add_to_order_html, name='add_to_order'),
    path('estimation_infusion_speed/', views.estimation_infusion_speed, name='estimation_infusion_speed'),
    path('estimation_infusion_speed/<int:order_id>/', views.estimation_infusion_speed, name='estimation_infusion_speed_with_id'),
    path('update_order_params/<int:order_id>/', views.update_order_params, name='update_order_params'),
    path('complete_order/<int:order_id>/', views.complete_order_html, name='complete_order'),
    path('delete_order/<int:order_id>/', views.delete_order_html, name='delete_order'),
    
    path('api/', include(router.urls)),
    
    path('api/drugs/', views.DrugList.as_view(), name='drug-list'),
    path('api/drugs/<int:pk>/', views.DrugDetail.as_view(), name='drug-detail'),
    path('api/drugs/<int:pk>/add-image/', views.add_drug_image, name='drug-add-image'),
    path('api/drugs/<int:pk>/add-to-order/', views.add_drug_to_order, name='drug-add-to-order'),
    
    path('api/orders/cart/', views.cart_icon, name='cart-icon'),
    path('api/orders/', views.OrderList.as_view(), name='order-list'),
    path('api/orders/<int:pk>/', views.OrderDetail.as_view(), name='order-detail'),
    path('api/orders/<int:pk>/form/', views.form_order, name='order-form'),
    path('api/orders/<int:pk>/complete/', views.complete_order, name='order-complete'),
    path('api/orders/<int:pk>/reject/', views.reject_order, name='order-reject'),
    
    path('api/orders/<int:order_pk>/drugs/<int:drug_pk>/', views.drug_in_order_actions, name='drug-in-order'),
    
    path('api/register/', views.UserRegistration.as_view(), name='user-register'),
    path('api/profile/<int:pk>/', views.UserProfile.as_view(), name='user-profile'),
    path('api/login/', views.user_login, name='user-login'),
    path('api/logout/', views.user_logout, name='user-logout'),
    
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json-file'),
]
