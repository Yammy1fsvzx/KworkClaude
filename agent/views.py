from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from datetime import datetime
import mimetypes
import os
from .models import Document, Analysis
from .serializers import DocumentSerializer, AnalysisSerializer
from .services import ClaudeService
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Create your views here.

class DocumentViewSet(viewsets.ModelViewSet):
    """
    API для работы с документами.
    
    Позволяет загружать, просматривать, обновлять и удалять документы
    для последующего анализа с использованием Claude API.
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    
    @swagger_auto_schema(
        operation_summary='Получить список документов',
        operation_description='Возвращает список всех загруженных документов.',
        responses={200: DocumentSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """Получить список всех документов в системе."""
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary='Получить информацию о документе',
        operation_description='Возвращает детальную информацию об указанном документе.',
        responses={
            200: DocumentSerializer(), 
            404: 'Документ не найден'
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Получить детальную информацию об одном документе."""
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary='Загрузить документ',
        operation_description='Загружает новый документ в систему. Поддерживаемые форматы: PDF, DOCX, TXT, CSV, JSON, XLSX.',
        request_body=DocumentSerializer,
        responses={
            201: DocumentSerializer(),
            400: 'Ошибка валидации'
        }
    )
    def create(self, request, *args, **kwargs):
        """Загрузить новый документ в систему."""
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary='Удалить документ',
        operation_description='Удаляет указанный документ из системы.',
        responses={
            204: 'Документ успешно удален',
            404: 'Документ не найден'
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Удалить документ из системы."""
        return super().destroy(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        file = self.request.FILES.get('file')
        file_name = file.name
        
        # Используем имя файла в качестве имени документа, если оно не указано
        name = serializer.validated_data.get('name')
        if not name:
            # Удаляем расширение из имени файла для более красивого отображения
            name = os.path.splitext(file_name)[0]
        
        # Определяем тип файла из расширения и MIME-типа
        mime_type, _ = mimetypes.guess_type(file_name)
        file_extension = os.path.splitext(file_name)[1].lower()
        
        # Определение типа файла по расширению, если mime_type не определен
        if not mime_type:
            if file_extension == '.txt':
                mime_type = 'text/plain'
            elif file_extension == '.pdf':
                mime_type = 'application/pdf'
            elif file_extension == '.docx':
                mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            elif file_extension == '.xlsx':
                mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            elif file_extension == '.csv':
                mime_type = 'text/csv'
            elif file_extension == '.json':
                mime_type = 'application/json'
            else:
                mime_type = 'application/octet-stream'
        
        # Записываем тип в консоль для диагностики
        print(f"Загружен файл: {file_name}, тип: {mime_type}, имя документа: {name}")
        
        serializer.save(file_type=mime_type, name=name)

class AnalysisViewSet(viewsets.ModelViewSet):
    """
    API для работы с анализами документов.
    
    Позволяет создавать новые анализы, просматривать результаты существующих,
    а также повторять анализы в случае ошибок.
    """
    queryset = Analysis.objects.all()
    serializer_class = AnalysisSerializer
    
    @swagger_auto_schema(
        operation_summary='Получить список анализов',
        operation_description='Возвращает список всех анализов документов в системе.',
        responses={200: AnalysisSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """Получить список всех анализов в системе."""
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary='Получить результаты анализа',
        operation_description='Возвращает детальную информацию о конкретном анализе, включая результаты.',
        responses={
            200: AnalysisSerializer(), 
            404: 'Анализ не найден'
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Получить детальную информацию об одном анализе, включая результаты."""
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary='Создать новый анализ',
        operation_description="""
        Создает новый анализ для указанных документов.
        
        Для создания анализа необходимо указать:
        - document_ids: список UUID документов для анализа (минимум 1 документ)
        - custom_prompt: (опционально) пользовательский запрос для анализа
        
        Система автоматически запустит обработку документов с использованием API Claude.
        """,
        request_body=AnalysisSerializer,
        responses={
            201: AnalysisSerializer(),
            400: 'Ошибка валидации'
        }
    )
    def create(self, request, *args, **kwargs):
        """Создать новый анализ для указанных документов."""
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary='Удалить анализ',
        operation_description='Удаляет указанный анализ из системы.',
        responses={
            204: 'Анализ успешно удален',
            404: 'Анализ не найден'
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Удалить анализ из системы."""
        return super().destroy(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary='Повторить анализ',
        operation_description='Сбрасывает статус анализа и запускает его повторно с теми же параметрами.',
        responses={
            200: AnalysisSerializer(),
            404: 'Анализ не найден'
        }
    )
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """
        Повторить анализ документов.
        
        Сбрасывает результаты и статус анализа, затем запускает
        процесс анализа заново с теми же документами и параметрами.
        Полезно в случае ошибок при первоначальном анализе.
        """
        analysis = self.get_object()
        analysis.status = 'pending'
        analysis.result = None
        analysis.completed_at = None
        analysis.save()
        
        self.run_analysis(analysis)
        return Response(self.get_serializer(analysis).data)
    
    def perform_create(self, serializer):
        analysis = serializer.save(status='pending')
        self.run_analysis(analysis)
        
    def run_analysis(self, analysis):
        try:
            # Update status to processing
            analysis.status = 'processing'
            analysis.save()
            
            # Get documents
            documents = analysis.documents.all()
            
            if not documents:
                analysis.status = 'failed'
                analysis.result = "No documents provided for analysis"
                analysis.save()
                return
            
            # Process documents with Claude
            claude_service = ClaudeService()
            result = claude_service.compare_documents(
                documents=documents,
                custom_prompt=analysis.custom_prompt
            )
            
            # Update analysis with results
            analysis.result = result
            analysis.status = 'completed'
            analysis.completed_at = datetime.now()
            analysis.save()
            
        except Exception as e:
            analysis.status = 'failed'
            analysis.result = f"Analysis failed: {str(e)}"
            analysis.save()
