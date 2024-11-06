# views.py
from .models import Topic
from .forms import LessonForm
from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from .models import Lesson, Topic, Test, Theory
from django.http import JsonResponse
import json
import ast

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
            # Преобразует строку в список словарей
            answers = json.loads(test.answer)
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


def create_lesson(request):
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            topic = form.cleaned_data['topic']
            theory_content = request.POST.get('theory')

            # Создаем новый урок
            lesson = Lesson.objects.create(title=title, topic=topic)
            if theory_content:
                Theory.objects.create(lesson=lesson, title=f'Теория для {title}', content=theory_content)

            # Получаем данные тестов и ответов из POST-запроса
            test_titles = request.POST.getlist('test-titles[]')
            tests = request.POST.getlist('tests[]')

            # Сохраняем тесты и ответы
            for i, test_title in enumerate(test_titles):
                if test_title:
                    question = tests[i]
                    correct_answer_index = request.POST.get(f'correct-answer-{i}')
                    correct_answer_text = None

                    # Получаем текст правильного ответа
                    if correct_answer_index is not None:
                        correct_answer_index = int(correct_answer_index)
                        correct_answer_text = request.POST.getlist(f'answers[{i}][]')[correct_answer_index]

                    # Получаем ответы для текущего теста
                    test_answers = request.POST.getlist(f'answers[{i}][]')
                    formatted_answers = [{'text': answer, 'is_correct': answer == correct_answer_text} 
                                         for answer in test_answers if answer]

                    json_ans = json.dumps(formatted_answers)
                    Test.objects.create(lesson=lesson, title=test_title, question=question, answer=json_ans)

            return redirect('home')
    else:
        form = LessonForm()

    return render(request, 'lesson_creation.html', {'form': form})