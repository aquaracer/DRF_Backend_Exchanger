from django.urls import path

from finance import views

urlpatterns = [
    path("get_rates/", views.get_rates),
]
