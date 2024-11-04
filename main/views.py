# views.py
from django.shortcuts import render, get_object_or_404
from .models import Lesson, Topic # Импортируйте вашу модель Lesson
import ast
from django.http import JsonResponse


def home_view(request):
    # Получаем все темы из базы данных
    topics = Topic.objects.all()
    
    # Передаем данные в шаблон
    context = {
        'topics': topics
    }
    
    return render(request, 'home.html', context)


def lesson_detail_view(request, lesson_id):
    # Получаем урок по ID
    lesson = get_object_or_404(Lesson, id=lesson_id)
    theories = lesson.theories.all()  # Получаем все теории, связанные с уроком
    tests = lesson.tests.all()  # Получаем все тесты, связанные с уроком
    serialized_tests = []
    for test in tests:
        try:
            # Используем ast.literal_eval для безопасного преобразования строки в объект Python
            answers = ast.literal_eval(test.answer)  # Преобразует строку в список словарей
        except (ValueError, SyntaxError) as e:
            return JsonResponse({'error': 'Invalid format', 'details': str(e)}, status=400)

        serialized_tests.append({
            'id': test.id,
            'title': test.title,
            'question': test.question,
            'answers': answers
        })

    # Передаем данные в шаблон
    context = {
        'lesson': lesson,
        'theories': theories,
        'tests': serialized_tests
    }

    return render(request, 'lesson.html', context)
