from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User 
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Tarefa, PerfilUsuario


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Usuário ou senha incorretos.")

    return render(request, "login.html")


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            return render(request, 'register.html', {'error': 'As senhas não coincidem.'})
        
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Usuário já existe.'})
        
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        return redirect('login')
    
    return render(request, "register.html")


@login_required
def home(request):

    usuario = request.user
    perfil, created = PerfilUsuario.objects.get_or_create(usuario=usuario)

    if request.method == 'POST':
        # ADICIONAR TAREFA
        if 'add' in request.POST:
            titulo = request.POST['titulo']
            descricao = request.POST['descricao']
            Tarefa.objects.create(
                usuario=usuario,
                titulo=titulo,
                descricao=descricao
            )

        # CONCLUIR TAREFA
        elif 'done' in request.POST:
            tarefa_id = request.POST['tarefa_id']
            tarefa = Tarefa.objects.get(id=tarefa_id)

            tarefa.concluida = True
            tarefa.data_conclusao = timezone.now()
            tarefa.save()

            hoje = timezone.now().date()

            if perfil.ultima_conclusao == hoje - timezone.timedelta(days=1):
                perfil.dias_consecutivos += 1
            elif perfil.ultima_conclusao != hoje:
                perfil.dias_consecutivos = 1

            perfil.xp += 10
            perfil.ultima_conclusao = hoje
            perfil.save()

        # EXCLUIR TAREFA
        elif 'delete' in request.POST:
            tarefa_id = request.POST['tarefa_id']
            Tarefa.objects.get(id=tarefa_id).delete()

    tarefas = Tarefa.objects.filter(usuario=usuario).order_by('-data_criacao')

    return render(request, 'home.html', {
        'tarefas': tarefas,
        'perfil': perfil
    })
