from django.db import models


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


class Image(models.Model):
    theory = models.ForeignKey('Theory', on_delete=models.CASCADE,
                               related_name='image_set', null=True, blank=True)  # Связь с Theory
    test = models.ForeignKey('Test', on_delete=models.CASCADE,
                             related_name='image_set', null=True, blank=True)  # Связь с Test
    image = models.ImageField(upload_to='theory_images/')

    def __str__(self):
        return f"Image {self.id}"


class Theory(models.Model):
    lesson = models.ForeignKey(
        Lesson, related_name='theories', on_delete=models.CASCADE)
    # Добавлено поле для названия теории
    title = models.CharField(max_length=255)
    content = models.TextField()


class Test(models.Model):
    lesson = models.ForeignKey(
        Lesson, related_name='tests', on_delete=models.CASCADE)
    # Добавлено поле для названия теста
    title = models.CharField(max_length=255)
    question = models.CharField(max_length=255)
    answer = models.TextField()
