from django.shortcuts import redirect, render
from django.http.response import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_django
from django.contrib import messages

def cadastro(request):
    if request.method =="GET":
        return render(request, 'cadastro.html') 
    else:
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        
        user = User.objects.filter(username=username).first()

        if user:
            mensagem = 'Já existe um usuario com esse username'
            context={
                'mensagem':mensagem
            }
            return render(request, 'cadastro.html', contex )
        
        user = User.objects.create_user(username=username, email=email, password=senha)
        user.save()
        return render(request, 'login.html')

def login(request):
    if request.method =="GET":
        return render(request, 'login.html')
    else:
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = authenticate(username=username, password=senha)

        if user:
            login_django(request, user)
            return redirect('inicial')
        else:
            mensagem =('Login ou senha inválidos')
            context={
                'mensagem':mensagem
            }
            return render(request, 'login.html', context)
# Create your views here.
