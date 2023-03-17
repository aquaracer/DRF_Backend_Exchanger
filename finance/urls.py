from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('user_account', views.UserAccountListViewSet, basename='Accounts')
router.register('user_transaction', views.UserTransactionsViewSet, basename='Transaction')
router.register('admin_account', views.AdminTransactionsViewSet, basename='Administrator')
router.register('admin_transaction', views.AdminTransactionsViewSet, basename='Transaction')
router.register('user_application', views.UserApplicationViewSet, basename='Application')

urlpatterns = router.urls
