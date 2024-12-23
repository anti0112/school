# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Topic, Lesson, Theory, Question, Answer, UserAnswer
from .forms import LessonForm
import json


def home_view(request):
    topics = Topic.objects.prefetch_related('lessons').all()
    return render(request, 'home.html', {'topics': topics})


def lesson_detail_view(request, lesson_id):
    lesson = get_object_or_404(Lesson.objects.prefetch_related(
        'theories',
        'questions',
        'questions__answers',
        'questions__images'
    ), id=lesson_id)

    questions = []
    for question in lesson.questions.all():
        question_data = {
            'id': question.id,
            'text': question.text,
            'type': question.question_type,
            'explanation': question.explanation,
            'additional_data': question.additional_data,
            'answers': []
        }

        # Подготавливаем ответы в зависимости от типа вопроса
        if question.question_type in ['single', 'multiple']:
            question_data['answers'] = list(question.answers.values(
                'id', 'text', 'is_correct'
            ))
        elif question.question_type == 'ordering':
            question_data['answers'] = list(question.answers.order_by('order').values(
                'id', 'text', 'order'
            ))
        elif question.question_type == 'matching':
            question_data['answers'] = list(question.answers.values(
                'id', 'text', 'matching_pair_id'
            ))
        elif question.question_type == 'drag_drop':
            question_data['answers'] = list(question.answers.values(
                'id', 'text', 'position_data'
            ))
        elif question.question_type == 'text':
            question_data['answers'] = [{'id': ans.id, 'text': ans.text} 
                                      for ans in question.answers.all()]

        questions.append(question_data)

    context = {
        'lesson': lesson,
        'theories': lesson.theories.all(),
        'questions': questions
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
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    try:
        data = json.loads(request.body)
        question_id = data.get('question_id')
        user_answer_data = data.get('answer')

        question = get_object_or_404(Question, id=question_id)
        
        # Создаем запись об ответе пользователя
        user_answer = UserAnswer(
            user=request.user,
            question=question,
            answer_data=user_answer_data
        )

        if question.question_type in ['single', 'multiple']:
            selected_answers = Answer.objects.filter(id__in=user_answer_data)
            user_answer.selected_answers.set(selected_answers)
        elif question.question_type == 'text':
            user_answer.text_answer = user_answer_data

        user_answer.save()  # Здесь автоматически вызовется check_answer

        response_data = {
            'is_correct': user_answer.is_correct,
            'explanation': question.explanation if user_answer.is_correct else None
        }

        return JsonResponse(response_data)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


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