from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view
from .yasg import urlpatterns as doc_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('finance.urls')),
    path('health/', TemplateView.as_view(template_name='health.html'), name='health'),
    path('api/docs/', get_schema_view(
        title='DRF Backend Exchanger API',
        description='API documentation for DRF Backend Exchanger',
        version='1.0.0'
    ), name='openapi-schema'),
]

urlpatterns += doc_urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
