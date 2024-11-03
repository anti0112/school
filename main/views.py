# views.py
from django.shortcuts import render, get_object_or_404
from .models import Lesson  # Импортируйте вашу модель Lesson


def home_view(request):
    # Получаем все уроки из базы данных
    lessons = Lesson.objects.all()

    # Передаем данные в шаблон
    context = {
        'lessons': lessons
    }

    return render(request, 'home.html', context)


def lesson_detail_view(request, lesson_id):
    # Получаем урок по ID
    lesson = get_object_or_404(Lesson, id=lesson_id)
    theories = lesson.theories.all()  # Получаем все теории, связанные с уроком
    tests = lesson.tests.all()  # Получаем все тесты, связанные с уроком

    # Передаем данные в шаблон
    context = {
        'lesson': lesson,
        'theories': theories,
        'tests': tests
    }

    return render(request, 'lesson.html', context)
