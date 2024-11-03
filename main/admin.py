from django.contrib import admin
from .models import Lesson, Theory, Image, Test


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1  # Количество пустых форм для добавления новых изображений


class TheoryAdmin(admin.ModelAdmin):
    # Позволяет добавлять изображения прямо в форме теории
    inlines = [ImageInline]


class TestAdmin(admin.ModelAdmin):
    # Позволяет добавлять изображения прямо в форме теста
    inlines = [ImageInline]


# Регистрация моделей
admin.site.register(Lesson)
admin.site.register(Theory, TheoryAdmin)
admin.site.register(Image)
admin.site.register(Test, TestAdmin)
