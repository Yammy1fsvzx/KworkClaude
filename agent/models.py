from django.db import models
import uuid

class Document(models.Model):
    """
    Модель для хранения документов, загруженных в систему.
    
    Модель предоставляет возможность загрузки документов различных типов,
    которые впоследствии могут быть проанализированы с использованием API Claude.
    
    Входящие данные:
    - file: Файл документа (PDF, DOCX, TXT и т.д.)
    - name: Название документа (если не указано, будет использовано имя файла)
    - file_type: Тип файла определяется автоматически при загрузке
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="Идентификатор")
    file = models.FileField(upload_to='documents/', verbose_name="Файл")
    name = models.CharField(max_length=255, verbose_name="Название")
    file_type = models.CharField(max_length=50, verbose_name="Тип файла")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")
    
    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"
    
    def __str__(self):
        return self.name

class Analysis(models.Model):
    """
    Модель для хранения результатов анализа документов с использованием API Claude.
    
    Анализ может включать в себя сравнение нескольких документов, поиск ключевой информации,
    ответы на вопросы по содержанию документов и другие операции с использованием ИИ.
    
    Входящие данные:
    - documents: Связь со списком документов для анализа (минимум 1 документ)
    - custom_prompt: Пользовательский запрос для анализа (опционально)
    - status: Статус анализа устанавливается автоматически
    
    Выходные данные:
    - result: Текстовый результат анализа от API Claude
    - completed_at: Дата и время завершения анализа (заполняется автоматически)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="Идентификатор")
    documents = models.ManyToManyField(Document, related_name='analyses', verbose_name="Документы")
    result = models.TextField(blank=True, null=True, verbose_name="Результат")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата завершения")
    custom_prompt = models.TextField(blank=True, null=True, help_text="Пользовательский запрос для анализа документов. Оставьте пустым для использования стандартного промпта.", verbose_name="Пользовательский запрос")
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'В ожидании'),
            ('processing', 'В процессе'),
            ('completed', 'Завершен'),
            ('failed', 'Не удалось'),
        ],
        default='pending',
        verbose_name="Статус"
    )
    
    class Meta:
        verbose_name = "Анализ"
        verbose_name_plural = "Анализы"
    
    def __str__(self):
        return f"Анализ {self.id} - {self.status}"
