from django.contrib import admin
from .models import (
    Topic,
    Lesson,
    Theory,
    Image,
    Question,
    Answer,
    UserAnswer
)


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1
    classes = ['collapse']


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4
    classes = ['collapse']
    fields = ('text', 'is_correct', 'explanation', 'order', 'position_data', 'matching_pair')


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    classes = ['collapse']


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title', 'description')
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'description')
    list_filter = ('topic',)
    search_fields = ('title', 'description')


@admin.register(Theory)
class TheoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson')
    list_filter = ('lesson',)
    search_fields = ('title', 'content')
    inlines = [ImageInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'lesson', 'question_type', 'created_at')
    list_filter = ('question_type', 'lesson')
    search_fields = ('text', 'explanation')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [AnswerInline, ImageInline]
    fieldsets = (
        (None, {
            'fields': ('lesson', 'text', 'question_type')
        }),
        ('Дополнительная информация', {
            'classes': ('collapse',),
            'fields': ('explanation', 'additional_data')
        }),
        ('Метаданные', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct', 'order')
    list_filter = ('is_correct', 'question__question_type')
    search_fields = ('text', 'explanation')
    raw_id_fields = ('question', 'matching_pair')


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'is_correct', 'answered_at')
    list_filter = ('is_correct', 'question__question_type')
    search_fields = ('user__username', 'question__text')
    readonly_fields = ('is_correct', 'answered_at')
    raw_id_fields = ('user', 'question')
    filter_horizontal = ('selected_answers',)
    fieldsets = (
        (None, {
            'fields': ('user', 'question', 'selected_answers')
        }),
        ('Дополнительные данные', {
            'classes': ('collapse',),
            'fields': ('text_answer', 'answer_data')
        }),
        ('Результат', {
            'fields': ('is_correct', 'answered_at')
        }),
    )

    def has_add_permission(self, request):
        return False  # Запрещаем создание ответов через админку


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'theory', 'question', 'image')
    list_filter = ('theory', 'question')
    raw_id_fields = ('theory', 'question')
