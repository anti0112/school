# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth import authenticate
from rest_framework import generics
from .models import CustomUser
from .serializers import UserSerializer


class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        serializer = self.get_serializer(data=request.POST)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)  # Автоматический вход после регистрации
            return redirect('login')  # Перенаправление на страницу входа
        return render(request, 'register.html', {'serializer': serializer})


class LoginView(generics.GenericAPIView):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')  # Перенаправление на главную страницу
        return render(request, 'login.html', {'error': 'Неверный логин или пароль'})
