from django.views.generic import TemplateView, ListView, CreateView, DetailView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from .models import Document, Analysis
from .forms import DocumentUploadForm, AnalysisCreateForm
from .services import ClaudeService
from datetime import datetime
from django.views import View
from django.shortcuts import get_object_or_404
import os
from django.contrib import messages

class HomeView(TemplateView):
    template_name = 'agent/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documents_count'] = Document.objects.count()
        context['analyses_count'] = Analysis.objects.count()
        context['recent_analyses'] = Analysis.objects.all().order_by('-created_at')[:5]
        return context

class DocumentListView(ListView):
    model = Document
    template_name = 'agent/document_list.html'
    context_object_name = 'documents'
    ordering = ['-uploaded_at']

class DocumentUploadView(CreateView):
    model = Document
    form_class = DocumentUploadForm
    template_name = 'agent/document_upload.html'
    success_url = reverse_lazy('document_list')
    
    def form_valid(self, form):
        # Если имя не указано, используем имя файла (без расширения)
        if not form.cleaned_data.get('name'):
            uploaded_file = form.cleaned_data.get('file')
            file_name = uploaded_file.name
            # Удаляем расширение из имени файла для более красивого отображения
            form.instance.name = os.path.splitext(file_name)[0]
            print(f"Имя документа не указано, используем имя файла: {form.instance.name}")
        
        response = super().form_valid(form)
        messages.success(self.request, f'Документ "{self.object.name}" успешно загружен.')
        return response

class AnalysisCreateView(CreateView):
    model = Analysis
    form_class = AnalysisCreateForm
    template_name = 'agent/analysis_create.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documents'] = Document.objects.all().order_by('-uploaded_at')
        return context
    
    def form_valid(self, form):
        analysis = form.save(commit=False)
        analysis.status = 'processing'
        analysis.save()
        
        # Добавляем выбранные документы
        document_ids = self.request.POST.getlist('documents')
        analysis.documents.set(Document.objects.filter(id__in=document_ids))
        
        # Запускаем анализ
        try:
            documents = analysis.documents.all()
            
            if not documents:
                analysis.status = 'failed'
                analysis.result = "Документы для анализа не выбраны"
                analysis.save()
                return redirect('analysis_detail', pk=analysis.id)
            
            # Обрабатываем документы с помощью Claude
            claude_service = ClaudeService()
            result = claude_service.compare_documents(
                documents=documents,
                custom_prompt=form.cleaned_data.get('custom_prompt')
            )
            
            # Обновляем результаты анализа
            analysis.result = result
            analysis.status = 'completed'
            analysis.completed_at = datetime.now()
            analysis.save()
            
        except Exception as e:
            analysis.status = 'failed'
            analysis.result = f"Ошибка анализа: {str(e)}"
            analysis.save()
        
        return redirect('analysis_detail', pk=analysis.id)

class AnalysisDetailView(DetailView):
    model = Analysis
    template_name = 'agent/analysis_detail.html'
    context_object_name = 'analysis'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documents'] = self.object.documents.all()
        return context 

class RetryAnalysisView(View):
    """Представление для повторного запуска анализа"""
    
    def post(self, request, pk):
        analysis = get_object_or_404(Analysis, pk=pk)
        analysis.status = 'processing'
        analysis.result = None
        analysis.completed_at = None
        analysis.save()
        
        # Запускаем анализ заново
        try:
            documents = analysis.documents.all()
            
            if not documents:
                analysis.status = 'failed'
                analysis.result = "Документы для анализа не выбраны"
                analysis.save()
                return redirect('analysis_detail', pk=analysis.id)
            
            # Обрабатываем документы с помощью Claude
            claude_service = ClaudeService()
            result = claude_service.compare_documents(
                documents=documents,
                custom_prompt=analysis.custom_prompt
            )
            
            # Обновляем результаты анализа
            analysis.result = result
            analysis.status = 'completed'
            analysis.completed_at = datetime.now()
            analysis.save()
            
        except Exception as e:
            analysis.status = 'failed'
            analysis.result = f"Ошибка анализа: {str(e)}"
            analysis.save()
        
        return redirect('analysis_detail', pk=analysis.id) 