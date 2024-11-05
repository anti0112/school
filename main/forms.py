# main/forms.py
from django import forms
from .models import Topic

class LessonForm(forms.Form):
    title = forms.CharField(max_length=200, label='Название урока')
    topic = forms.ModelChoiceField(queryset=Topic.objects.all(), label='Выберите тему')
    theory = forms.CharField(widget=forms.Textarea, label='Теоретический материал', required=False)
    tests = forms.CharField(widget=forms.Textarea, label='Тесты', required=False)