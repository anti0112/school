from django.db import models


class Lesson(models.Model):
    title = models.CharField(max_length=200)  # Название урока
    description = models.TextField()  # Описание урока

    def __str__(self):
        return self.title


# class Image(models.Model):
#     image = models.ImageField(upload_to='theory_images/')

#     def __str__(self):
#         return f"Image {self.id}"

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
        Lesson, on_delete=models.CASCADE, related_name='theories')
    content = models.TextField()  # Содержимое теории
    images = models.ManyToManyField(Image, related_name='theories', blank=True)

    def __str__(self):
        return f"Theory for {self.lesson.title}"


class Test(models.Model):
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name='tests')
    question = models.CharField(max_length=255)  # Вопрос теста
    answer = models.TextField()  # answers=[
    # {"text": "Хранит данные.", "is_correct": True},

    images = models.ManyToManyField(
        Image, related_name='tests', blank=True)  # Связь с изображениями

    def __str__(self):
        return f"Test for {self.lesson.title}: {self.question}"
