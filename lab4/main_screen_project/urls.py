from django.urls import path, include
from rest_framework.routers import DefaultRouter
from main_screen import views  # Импортируем views из main_screen
from rest_framework import permissions, routers
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

router = DefaultRouter()
router.register(r'rent_services', views.RentServiceViewSet, basename='rent_service')
router.register(r'user', views.UserViewSet, basename='user')

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    
    path('rent_services/', views.rent_list, name='rent-service-list'),          # GET список услуг
    path('rent_services/<int:pk>/', views.Get_Service, name='rent-service-detail'),  # GET одна запись
    path('rent_services/add/', views.add_Service, name='rent-service-add'),       # POST добавление
    path('rent_services/<int:pk>/edit/', views.Change_Service, name='rent-service-update'),  # PUT изменение
    path('rent_services/<int:pk>/delete/', views.Delete_Service, name='rent-service-delete'),  # DELETE удаление
    path('rent_services/<int:pk>/add_to_draft/', views.CreateRentOrder, name='rent-service-add-to-draft'),  # POST добавление в заявку-черновик
    path('rent_services/<int:pk>/add_image/', views.load_image_to_minio, name='rent-service-add-image'),  # POST добавление изображения

    path('rent_orders/', views.list_order, name='rent-order-list'),  # GET список
    path('rent_orders/<int:pk>/', views.get_order, name='rent-order-detail'),  # GET одна запись **
    path('rent_orders/<int:pk>/edit/', views.change_order, name='rent-order-update'),  # PUT изменение
    path('rent_orders/<int:pk>/finalize/', views.finalize_order, name='rent-order-finalize'),  # PUT завершение
    path('rent_orders/<int:pk>/reject/', views.rejecting_order, name='rent-order-reject'),  # PUT отклонение
    path('rent_orders/<int:pk>/del', views.delete_order, name='rent-order-delete'),  # DELETE удаление
    
    path('rent_orders/<int:ok>/services/<int:sk>/delete/', views.delete_service_from_order, name='rent-order-service-delete'),  # DELETE удаление услуги из заявки
    path('rent_orders/<int:ok>/services/<int:sk>/update_reading/', views.change_shipping_cargo, name='rent-order-service-update-reading'),  # PUT изменение current_reading

   #  path('register/', views.UserRegistrationView.as_view(), name='user-register'),  # POST регистрация
   #  path('profile/update/', views.UserProfileUpdateView.as_view(), name='user-profile-update'),  # PUT личный кабинет
   #  path('login/', views.UserLoginView.as_view(), name='user-login'),  # POST аутентификация
   #  path('logout/', views.UserLogoutView.as_view(), name='user-logout'),  # POST деавторизация
   path('create_user/', views.create_user, name='create_user'),

   path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
   path('login',  views.login_view, name='login'),
   path('logout', views.logout_view, name='logout'),
]
