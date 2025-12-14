from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drugs_estimation import views
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
    path('', views.search, name='search'),
    path('vasoactive_drug/<int:drug_id>/', views.vasoactive_drug_detail, name='vasoactive_drug_detail'),
    path('add_to_estimation_request/<int:drug_id>/', views.add_to_estimation_request_html, name='add_to_estimation_request'),
    path('estimation_infusion_speed/', views.estimation_infusion_speed, name='estimation_infusion_speed'),
    path('estimation_infusion_speed/<int:estimation_request_id>/', views.estimation_infusion_speed, name='estimation_infusion_speed_with_id'),
    path('update_estimation_request_params/<int:estimation_request_id>/', views.update_estimation_request_params, name='update_estimation_request_params'),
    path('complete_estimation_request/<int:estimation_request_id>/', views.complete_estimation_request_html, name='complete_estimation_request'),
    path('delete_estimation_request/<int:estimation_request_id>/', views.delete_estimation_request_html, name='delete_estimation_request'),
    
    path('api/', include(router.urls)),
    
    path('api/drugs/', views.DrugList.as_view(), name='drug-list'),
    path('api/drugs/<int:pk>/', views.DrugDetail.as_view(), name='drug-detail'),
    path('api/drugs/<int:pk>/add-image/', views.add_drug_image, name='drug-add-image'),
    path('api/drugs/<int:pk>/add-to-estimation-request/', views.add_drug_to_estimation_request, name='drug-add-to-estimation-request'),
    
    path('api/estimation_requests/cart/', views.cart_icon, name='cart-icon'),
    path('api/estimation_requests/', views.EstimationRequestList.as_view(), name='estimation-request-list'),
    path('api/estimation_requests/<int:pk>/', views.EstimationRequestDetail.as_view(), name='estimation-request-detail'),
    path('api/estimation_requests/<int:pk>/form/', views.form_estimation_request, name='estimation-request-form'),
    path('api/estimation_requests/<int:pk>/complete/', views.complete_estimation_request, name='estimation-request-complete'),
    
    path('api/estimation_requests/<int:estimation_request_pk>/drugs/<int:drug_pk>/', views.drug_in_estimation_actions, name='drug-in-estimation'),
    path('api/estimation_requests/<int:pk>/update_results/', views.update_async_results, name='update-async-results'),
    
   path('api/laboratory_users/register/', views.UserRegistration.as_view(), name='laboratory-user-register'),
   path('api/laboratory_users/profile/<int:pk>/', views.UserProfile.as_view(), name='laboratory-user-profile'),
   path('api/laboratory_users/login/', views.user_login, name='laboratory-user-login'),
   path('api/laboratory_users/logout/', views.user_logout, name='laboratory-user-logout'),
    
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json-file'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'drugs_estimation' / 'static')
