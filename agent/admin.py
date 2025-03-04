from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from django.urls import path
from django.shortcuts import render
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from .models import Document, Analysis

# Функция для создания дашборда
def admin_dashboard(request):
    # Сбор статистики для дашборда
    total_documents = Document.objects.count()
    total_analyses = Analysis.objects.count()
    
    # Статистика за последнюю неделю
    last_week = timezone.now() - timezone.timedelta(days=7)
    documents_last_week = Document.objects.filter(uploaded_at__gte=last_week).count()
    analyses_last_week = Analysis.objects.filter(created_at__gte=last_week).count()
    
    # Статусы анализов
    completed_analyses = Analysis.objects.filter(status='completed').count()
    processing_analyses = Analysis.objects.filter(status='processing').count()
    pending_analyses = Analysis.objects.filter(status='pending').count()
    failed_analyses = Analysis.objects.filter(status='failed').count()
    
    # Распределение по типам документов
    document_types = Document.objects.values('file_type').annotate(count=Count('id')).order_by('-count')
    
    # Недавние документы и анализы
    recent_documents = Document.objects.all().order_by('-uploaded_at')[:5]
    recent_analyses = Analysis.objects.all().order_by('-created_at')[:5]
    
    return render(request, 'admin/dashboard.html', {
        'total_documents': total_documents,
        'total_analyses': total_analyses,
        'documents_last_week': documents_last_week,
        'analyses_last_week': analyses_last_week,
        'completed_analyses': completed_analyses,
        'processing_analyses': processing_analyses,
        'pending_analyses': pending_analyses,
        'failed_analyses': failed_analyses,
        'document_types': document_types,
        'recent_documents': recent_documents,
        'recent_analyses': recent_analyses,
    })

# Переопределение AdminSite для добавления дашборда
class ClaudeAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(admin_dashboard), name='dashboard'),
        ]
        return custom_urls + urls

# Создание экземпляра админ сайта
admin_site = ClaudeAdminSite(name='claude_admin')

# Оставляем стандартную регистрацию для Django-admin
@admin.register(Document)
class DocumentAdmin(ModelAdmin):
    list_display = ('name', 'file_type', 'uploaded_at')
    list_filter = ('file_type', 'uploaded_at')
    search_fields = ('name',)
    date_hierarchy = 'uploaded_at'
    list_per_page = 15
    
    # Кастомизация для unfold
    fieldsets = (
        ('Информация о документе', {
            'fields': ('name', 'file', 'file_type'),
            'classes': ('grid-col-12', 'grid-col-6@md', 'grid-col-4@lg')
        }),
        ('Метаданные', {
            'fields': ('uploaded_at',),
            'classes': ('grid-col-12', 'grid-col-6@md')
        }),
    )
    
    readonly_fields = ('uploaded_at', 'file_type')

class DocumentInline(TabularInline):
    model = Analysis.documents.through
    extra = 0

@admin.register(Analysis)
class AnalysisAdmin(ModelAdmin):
    list_display = ('id', 'status', 'created_at', 'completed_at', 'document_count')
    list_filter = ('status', 'created_at')
    date_hierarchy = 'created_at'
    readonly_fields = ('id', 'created_at', 'completed_at', 'result')
    exclude = ('documents',)
    list_per_page = 10
    inlines = [DocumentInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('id', 'status', 'created_at', 'completed_at'),
            'classes': ('grid-col-12',)
        }),
        ('Запрос', {
            'fields': ('custom_prompt',),
            'classes': ('grid-col-12',)
        }),
        ('Результат анализа', {
            'fields': ('result',),
            'classes': ('grid-col-12',)
        }),
    )
    
    def document_count(self, obj):
        return obj.documents.count()
    document_count.short_description = 'Документов'

# Регистрация модели в кастомном сайте
admin_site.register(Document, DocumentAdmin)
admin_site.register(Analysis, AnalysisAdmin)
