from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register("accounts", views.AdminAccountsViewSet, basename="AdminAccounts")
router.register(
    "transactions", views.AdminTransactionsViewSet, basename="AdminTransactions"
)

urlpatterns = router.urls
