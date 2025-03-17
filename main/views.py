# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Topic, Lesson, Theory, Question, Answer, UserAnswer
from .forms import LessonForm
import json


def home_view(request):
    topics = Topic.objects.prefetch_related('lessons').all()
    return render(request, 'home.html', {'topics': topics})


def lesson_view(request, lesson_id):
    """Отображение урока с теорией и тестами"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    theories = Theory.objects.filter(lesson=lesson)
    questions = Question.objects.filter(lesson=lesson).prefetch_related('answers')
    
    # Подготавливаем данные для каждого вопроса
    formatted_questions = []
    for question in questions:
        question_data = {
            'id': question.id,
            'title': f"Вопрос {len(formatted_questions) + 1}",
            'text': question.text,
            'type': question.question_type,
            'answers': list(question.answers.values('id', 'text')),
            'explanation': question.explanation
        }
        formatted_questions.append(question_data)

    context = {
        'lesson': lesson,
        'theories': theories,
        'tests': formatted_questions,
    }
    
    return render(request, 'lesson.html', context)


def create_lesson(request):
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save()

            # Создаем теорию
            theory_content = request.POST.get('theory')
            if theory_content:
                Theory.objects.create(
                    lesson=lesson,
                    title=f'Теория для {lesson.title}',
                    content=theory_content
                )

            # Создаем вопросы
            questions_data = json.loads(request.POST.get('questions', '[]'))
            for q_data in questions_data:
                question = Question.objects.create(
                    lesson=lesson,
                    text=q_data['text'],
                    question_type=q_data['type'],
                    explanation=q_data.get('explanation', ''),
                    additional_data=q_data.get('additional_data')
                )

                # Создаем ответы в зависимости от типа вопроса
                if q_data['type'] in ['single', 'multiple']:
                    for ans in q_data['answers']:
                        Answer.objects.create(
                            question=question,
                            text=ans['text'],
                            is_correct=ans['is_correct']
                        )
                elif q_data['type'] == 'ordering':
                    for i, ans in enumerate(q_data['answers']):
                        Answer.objects.create(
                            question=question,
                            text=ans['text'],
                            order=i
                        )
                elif q_data['type'] in ['matching', 'drag_drop']:
                    for ans in q_data['answers']:
                        Answer.objects.create(
                            question=question,
                            text=ans['text'],
                            position_data=ans.get('position_data'),
                            matching_pair_id=ans.get('matching_pair_id')
                        )

            return redirect('lesson_detail', lesson_id=lesson.id)
    else:
        form = LessonForm()

    return render(request, 'lesson_creation.html', {'form': form})


@csrf_exempt
def check_answers(request):
    """API эндпоинт для проверки ответов"""
    try:
        data = json.loads(request.body)
        results = {}
        
        for test_id, answer_id in data.items():
            question = get_object_or_404(Question, id=test_id)
            
            # Создаем или обновляем ответ пользователя
            user_answer, created = UserAnswer.objects.get_or_create(
                user=request.user,
                question=question,
                defaults={'text_answer': '', 'is_correct': False}
            )
            
            # Очищаем предыдущие выбранные ответы
            user_answer.selected_answers.clear()
            
            if question.question_type == 'single':
                selected_answer = get_object_or_404(Answer, id=answer_id)
                user_answer.selected_answers.add(selected_answer)
                
                # Сохраняем и проверяем ответ
                user_answer.save()
                
                results[test_id] = {
                    'correct': user_answer.is_correct,
                    'explanation': question.explanation if question.explanation else None
                }
            
            # Здесь можно добавить обработку других типов вопросов
            
        return JsonResponse({'results': results})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def user_progress(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    user_stats = UserAnswer.objects.filter(user=request.user).aggregate(
        total_answers=models.Count('id'),
        correct_answers=models.Count('id', filter=models.Q(is_correct=True))
    )

    # Добавляем процент правильных ответов
    total = user_stats['total_answers']
    if total > 0:
        user_stats['success_rate'] = (user_stats['correct_answers'] / total) * 100
    else:
        user_stats['success_rate'] = 0

    return JsonResponse(user_stats)


# def lesson_detail_view(request, lesson_id):
#     """Отображение деталей урока"""
#     lesson = get_object_or_404(Lesson, id=lesson_id)
#     return render(request, 'lesson_detail.html', {'lesson': lesson})