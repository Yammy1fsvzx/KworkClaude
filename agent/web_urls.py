from django.urls import path
from .web_views import (
    HomeView, 
    DocumentListView, 
    DocumentUploadView, 
    AnalysisCreateView,
    AnalysisDetailView,
    RetryAnalysisView
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('documents/', DocumentListView.as_view(), name='document_list'),
    path('documents/upload/', DocumentUploadView.as_view(), name='document_upload'),
    path('analyses/create/', AnalysisCreateView.as_view(), name='analysis_create'),
    path('analyses/<uuid:pk>/', AnalysisDetailView.as_view(), name='analysis_detail'),
    path('analyses/<uuid:pk>/retry/', RetryAnalysisView.as_view(), name='retry'),
] 