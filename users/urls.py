from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("profile", views.UserAreaViewSet, basename="")
router.register("accounts", views.UserAccountListViewSet, basename="Accounts")
router.register(
    "transactions", views.UserTransactionsViewSet,
    basename="UserTransactions"
)
router.register("applications", views.UserApplicationViewSet, basename="Application")

urlpatterns = router.urls

urlpatterns += [
    path("signup", views.UserSignupView.as_view()),
]
