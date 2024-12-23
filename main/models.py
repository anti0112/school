from django.db import models
from django.core.exceptions import ValidationError


class Topic(models.Model):
    title = models.CharField(max_length=255)  # Название темы
    description = models.TextField(blank=True)  # Описание темы (необязательно)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    title = models.CharField(max_length=200)  # Название урока
    description = models.TextField()  # Описание урока
    topic = models.ForeignKey(
        Topic, related_name='lessons', on_delete=models.CASCADE)  # Связь с темой

    def __str__(self):
        return self.title


class Theory(models.Model):
    lesson = models.ForeignKey(
        Lesson, related_name='theories', on_delete=models.CASCADE)
    # Добавлено поле для названия теории
    title = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return self.title


class QuestionType(models.TextChoices):
    SINGLE_CHOICE = 'single', 'Выбор одного варианта'
    MULTIPLE_CHOICE = 'multiple', 'Выбор нескольких вариантов'
    ORDERING = 'ordering', 'Расположить в правильном порядке'
    MATCHING = 'matching', 'Сопоставление'
    DRAG_DROP = 'drag_drop', 'Перетаскивание'
    TEXT_INPUT = 'text', 'Ввод текста'


class Question(models.Model):
    lesson = models.ForeignKey(
        Lesson, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
        default=QuestionType.SINGLE_CHOICE
    )
    explanation = models.TextField(blank=True, help_text="Объяснение правильного ответа")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Дополнительные данные для специфических типов вопросов
    additional_data = models.JSONField(
        null=True, 
        blank=True,
        help_text="Дополнительные данные для специфических типов вопросов"
    )

    def __str__(self):
        return f"{self.get_question_type_display()}: {self.text}"

    def clean(self):
        if self.question_type == QuestionType.MATCHING and not self.additional_data:
            raise ValidationError(
                "Для вопроса на сопоставление необходимо указать пары для сопоставления"
            )


class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    explanation = models.TextField(blank=True)
    order = models.IntegerField(null=True, blank=True)
    position_data = models.JSONField(
        null=True, 
        blank=True,
        help_text="Координаты или другие данные о позиции"
    )
    matching_pair = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='matched_with'
    )

    class Meta:
        ordering = ['order']

    def clean(self):
        if self.question.question_type == 'single':
            # Проверяем, есть ли уже правильный ответ
            if self.is_correct:
                existing_correct = self.question.answers.exclude(id=self.id).filter(is_correct=True)
                if existing_correct.exists():
                    raise ValidationError(
                        'В вопросе с одиночным выбором может быть только один правильный ответ'
                    )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.text} ({'Правильный' if self.is_correct else 'Неправильный'})"


class Image(models.Model):
    theory = models.ForeignKey(
        Theory, on_delete=models.CASCADE,
        related_name='images', null=True, blank=True)
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE,
        related_name='images', null=True, blank=True)
    image = models.ImageField(upload_to='content_images/')

    def __str__(self):
        return f"Image {self.id}"


class UserAnswer(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE)
    # Для разных типов ответов
    selected_answers = models.ManyToManyField(
        Answer,
        related_name='user_selections'
    )
    text_answer = models.TextField(blank=True)
    answer_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Дополнительные данные ответа (порядок, координаты и т.д.)"
    )
    is_correct = models.BooleanField()
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Пользователь может ответить на вопрос только один раз
        unique_together = ['user', 'question']

    def check_answer(self):
        """Проверка правильности ответа в зависимости от типа вопроса"""
        question_type = self.question.question_type
        
        if question_type == QuestionType.SINGLE_CHOICE:
            return self.selected_answers.filter(is_correct=True).exists()
            
        elif question_type == QuestionType.MULTIPLE_CHOICE:
            correct_answers = set(self.question.answers.filter(is_correct=True))
            selected_answers = set(self.selected_answers.all())
            return correct_answers == selected_answers
            
        elif question_type == QuestionType.ORDERING:
            correct_order = list(self.question.answers.values_list('order', flat=True))
            user_order = self.answer_data.get('order', [])
            return correct_order == user_order
            
        elif question_type == QuestionType.MATCHING:
            correct_pairs = {
                answer.id: answer.matching_pair_id 
                for answer in self.question.answers.all()
            }
            user_pairs = self.answer_data.get('matching', {})
            return correct_pairs == user_pairs
            
        elif question_type == QuestionType.DRAG_DROP:
            correct_positions = {
                answer.id: answer.position_data 
                for answer in self.question.answers.all()
            }
            user_positions = self.answer_data.get('positions', {})
            # Здесь можно добавить логику проверки с погрешностью
            return self._check_positions(correct_positions, user_positions)
            
        elif question_type == QuestionType.TEXT_INPUT:
            correct_answer = self.question.answers.first().text.lower()
            return self.text_answer.lower().strip() == correct_answer

    def save(self, *args, **kwargs):
        self.is_correct = self.check_answer()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.question.text[:30]}"
