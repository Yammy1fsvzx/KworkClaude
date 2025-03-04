"""
URL configuration for claude_agent project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Настройка Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="API Сервиса Claude Agent",
        default_version='v1',
        description="""
# API для сравнительного анализа документов с использованием Claude

Этот API предоставляет возможность:
- Загружать документы различных форматов (PDF, DOCX, TXT, CSV, JSON, XLSX)
- Создавать задания на анализ документов с использованием API Claude
- Получать результаты анализа в структурированном виде
- Отслеживать статус обработки заданий

## Как использовать API

### 1. Загрузка документов
Загрузите один или несколько документов с помощью POST-запроса на `/api/documents/`.
Для каждого документа вы получите уникальный идентификатор (UUID).
Имя документа можно указать в поле "name" или оставить пустым - тогда оно будет автоматически взято из имени файла.
Тип файла определяется автоматически.

```
POST /api/documents/
Content-Type: multipart/form-data

{
  "file": [бинарные данные файла],
  "name": "Финансовый отчет 2023.pdf" // Необязательное поле
}
```

### 2. Создание задания на анализ
Создайте задание на анализ с помощью POST-запроса на `/api/analyses/`.
Укажите идентификаторы документов в поле `document_ids` и опционально добавьте пользовательский 
запрос в поле `custom_prompt`.

```
POST /api/analyses/
Content-Type: application/json

{
  "document_ids": ["uuid1", "uuid2"],
  "custom_prompt": "Сравни эти документы и найди основные различия в финансовых показателях"
}
```

### 3. Получение результатов
Отслеживайте статус задания, отправляя GET-запрос на `/api/analyses/{id}/`.
Когда статус изменится на "completed", в поле `result` будет доступен результат анализа.

```
GET /api/analyses/[id]/
```

### 4. Повторение анализа
Если анализ завершился с ошибкой, вы можете повторить его, отправив POST-запрос на `/api/analyses/{id}/retry/`.

```
POST /api/analyses/[id]/retry/
```

## Коды ответов

- 200: Успешный запрос
- 201: Ресурс успешно создан
- 400: Ошибка в параметрах запроса
- 404: Ресурс не найден
- 500: Внутренняя ошибка сервера
        """,
        terms_of_service="https://www.example.com/policies/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("agent.urls")),
    
    # Swagger URLs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Главная страница
    path('', include('agent.web_urls')),
]

# Добавляем URL для медиа-файлов в режиме DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
