from django.urls import path
from . import views

urlpatterns = [
    path('lesson/<int:lesson_id>/', views.lesson_view, name='lesson_view'),
    path('api/check-answers/', views.check_answers, name='check_answers'),
]
