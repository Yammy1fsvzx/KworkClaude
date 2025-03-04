from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet, AnalysisViewSet

router = DefaultRouter()
router.register(r'documents', DocumentViewSet)
router.register(r'analyses', AnalysisViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 