from django import forms
from .models import Document, Analysis

class DocumentUploadForm(forms.ModelForm):
    name = forms.CharField(
        max_length=255, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя документа'})
    )
    
    class Meta:
        model = Document
        fields = ['file', 'name']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'})
        }

class AnalysisCreateForm(forms.ModelForm):
    custom_prompt = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Введите ваш запрос для анализа документов. Например: "Сравни эти два отчета и найди несоответствия" или "Посчитай, сколько раз встречается слово «проект»"'
        }),
        help_text='Оставьте поле пустым для использования стандартного сравнительного анализа.'
    )
    
    class Meta:
        model = Analysis
        fields = ['custom_prompt'] 