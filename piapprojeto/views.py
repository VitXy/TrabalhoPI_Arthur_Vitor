from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import Tarefa, PerfilUsuario


# ----------------- LOGIN -----------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Usuário ou senha incorretos.")

    return render(request, "login.html")


# ----------------- REGISTER -----------------
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
        PerfilUsuario.objects.create(usuario=user)

        return redirect('login')

    return render(request, 'register.html')


# ----------------- HOME / TAREFAS -----------------
@login_required
def home(request):

    usuario = request.user
    perfil, _ = PerfilUsuario.objects.get_or_create(usuario=usuario)

    tab = request.GET.get('tab', 'ativas')

    if request.method == 'POST':

        # ----------------- ADICIONAR -----------------
        if 'add' in request.POST:
            titulo = request.POST['titulo']
            descricao = request.POST.get('descricao', '')
            dificuldade = request.POST.get('dificuldade', 'M')

            Tarefa.objects.create(
                usuario=usuario,
                titulo=titulo,
                descricao=descricao,
                dificuldade=dificuldade
            )

        # ----------------- CONCLUIR -----------------
        elif 'done' in request.POST:
            tarefa_id = request.POST['tarefa_id']
            tarefa = Tarefa.objects.get(id=tarefa_id)

            if not tarefa.concluida:
                tarefa.concluida = True
                tarefa.data_conclusao = timezone.now()
                tarefa.save()

                xp = perfil.XP_BY_DIFFICULTY[tarefa.dificuldade]
                perfil.add_xp(xp)

        # ----------------- SOFT DELETE -----------------
        elif 'delete' in request.POST:
            tarefa = Tarefa.objects.get(id=request.POST['tarefa_id'])
            tarefa.is_deleted = True
            tarefa.deleted_at = timezone.now()
            tarefa.save()

        # ----------------- RESTAURAR -----------------
        elif 'restore' in request.POST:
            tarefa = Tarefa.objects.get(id=request.POST['tarefa_id'])
            tarefa.is_deleted = False
            tarefa.deleted_at = None
            tarefa.save()

    # ----------------- FILTRO DAS ABAS -----------------
    if tab == 'ativas':
        tarefas = Tarefa.objects.filter(
            usuario=usuario, concluida=False, is_deleted=False
        ).order_by('-data_criacao')

    elif tab == 'concluidas':
        tarefas = Tarefa.objects.filter(
            usuario=usuario, concluida=True, is_deleted=False
        ).order_by('-data_conclusao')

    elif tab == 'lixeira':
        tarefas = Tarefa.objects.filter(
            usuario=usuario, is_deleted=True
        ).order_by('-deleted_at')

    else:
        tarefas = []

    xp_needed = PerfilUsuario.xp_needed_for_level(perfil.level)
    xp_to_next = xp_needed - perfil.xp
    if xp_to_next < 0:
        xp_to_next = 0

    return render(request, "home.html", {
        "tarefas": tarefas,
        "perfil": perfil,
        "tab": tab,
        "xp": perfil.xp,
        "level": perfil.level,
        "xp_needed_for_level": xp_needed,
        "xp_to_next": xp_to_next,
    })


# ----------------- LOGOUT -----------------
def logout_view(request):
    logout(request)
    return redirect('login')
