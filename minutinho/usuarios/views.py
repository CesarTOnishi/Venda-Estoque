from django.shortcuts import redirect, render
from django.http.response import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

def cadastro(request):
    if request.method =="GET":
        return render(request, 'cadastro.html')
    else:
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        
        user = User.objects.filter(username=username).first()

        if user:
            return HttpResponse('Já Existe um usuario com esse username')
        
        user = User.objects.create_user(username=username, email=email, password=senha)
        user.save()
        return HttpResponse('Usuario cadastrado com Sucesso')

def login(request):
    if request.method =="GET":
        return render(request, 'login.html')
    else:
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = authenticate(username=username, password=senha)

        if user:
            return redirect('tela')
        else:
            return HttpResponse('Email ou senha inválidos')
# Create your views here.
