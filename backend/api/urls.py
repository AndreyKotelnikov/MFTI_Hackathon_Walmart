from django.urls import path, include
from api import views
from rest_framework.routers import DefaultRouter

app_name = 'api'

router = DefaultRouter()
router.register('predictions', views.SearchPredictionViewSet, basename='prediction')

urlpatterns = [
    path('', include(router.urls)),
    path('stores/list', views.StoreListView.as_view(), name='list_stores'),
]
