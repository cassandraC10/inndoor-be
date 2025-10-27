from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (DealViewSet, InspectionViewSet, LoginView, LogoutView,
                    MessageViewSet, NotificationViewSet, PropertyImageViewSet,
                    PropertyViewSet, RegisterView, ReviewViewSet,
                    SavedPropertyViewSet, UserProfileViewSet, UserView)

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet)
router.register(r'properties', PropertyViewSet)
router.register(r'property-images', PropertyImageViewSet)
router.register(r'inspections', InspectionViewSet)
router.register(r'deals', DealViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'messages', MessageViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'saved-properties', SavedPropertyViewSet)

schema_view = get_schema_view(
   openapi.Info(
      title="Inndoor Backend API",
      default_version='v1',
      description="API documentation for Inndoor platform",
      contact=openapi.Contact(email="support@inndoor.co"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    # DRF Router URLs
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', UserView.as_view(), name='me'),

    re_path(r'^docs(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
