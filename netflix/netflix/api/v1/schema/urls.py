from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from django.urls import path


urlpatterns = [
    path('', SpectacularAPIView.as_view(), name='schema'),
    path('redoc', SpectacularRedocView.as_view(url_name='v1:schema'), name='redoc'),
    path('swagger', SpectacularSwaggerView.as_view(url_name='v1:schema'), name='swagger'),
]
