from rest_framework import serializers
from .models import Document, Analysis

class DocumentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Document.
    
    Используется для преобразования объектов Document в JSON и обратно.
    
    Поля:
    - id: UUID документа (только для чтения)
    - file: Файл документа (обязательное поле при создании)
    - name: Название документа (опциональное, если не указано, используется имя файла)
    - file_type: Тип файла (только для чтения, определяется автоматически)
    - uploaded_at: Дата и время загрузки (только для чтения)
    """
    name = serializers.CharField(max_length=255, required=False)
    
    class Meta:
        model = Document
        fields = ['id', 'file', 'name', 'file_type', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at', 'file_type']

class AnalysisSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Analysis.
    
    Используется для преобразования объектов Analysis в JSON и обратно.
    
    Поля:
    - id: UUID анализа (только для чтения)
    - documents: Вложенное представление связанных документов (только для чтения)
    - document_ids: Список UUID документов для анализа (только для записи при создании)
    - custom_prompt: Пользовательский запрос для анализа (опционально)
    - result: Результат анализа (только для чтения)
    - created_at: Дата и время создания (только для чтения)
    - completed_at: Дата и время завершения (только для чтения)
    - status: Статус анализа (только для чтения)
    """
    documents = DocumentSerializer(many=True, read_only=True)
    document_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        help_text="Список UUID документов для анализа. Требуется минимум один документ."
    )
    
    class Meta:
        model = Analysis
        fields = ['id', 'documents', 'document_ids', 'custom_prompt', 'result', 'created_at', 'completed_at', 'status']
        read_only_fields = ['id', 'result', 'created_at', 'completed_at', 'status']
    
    def create(self, validated_data):
        """
        Создает новый объект Analysis и связывает его с указанными документами.
        
        Args:
            validated_data: Проверенные данные от сериализатора
            
        Returns:
            Analysis: Созданный объект анализа
        """
        document_ids = validated_data.pop('document_ids')
        analysis = Analysis.objects.create(**validated_data)
        analysis.documents.set(Document.objects.filter(id__in=document_ids))
        return analysis 