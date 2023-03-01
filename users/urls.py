from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('area', views.UserAreaViewSet, basename='area')

urlpatterns = router.urls

urlpatterns += [
    path('signup', views.UserSignupView.as_view()),
    path('connect_receipt_suborder', views.connect_receipt_suborder),
]
