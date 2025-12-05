from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Tarefa, PerfilUsuario
from django.contrib.auth.decorators import login_required
from django.utils import timezone


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
            return redirect('login')

    return render(request, 'login.html')


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Esse usuário já existe.")
            return redirect('register')

        user = User.objects.create_user(username=username, password=password)

        # cria perfil do usuário
        PerfilUsuario.objects.create(usuario=user)

        login(request, user)
        return redirect('home')

    return render(request, 'register.html')


@login_required
def home(request):

    perfil, created = PerfilUsuario.objects.get_or_create(usuario=request.user)

    # ======= TRATANDO POST (adicionar, concluir, excluir, restaurar) =======
    if request.method == "POST":

        # --- ADICIONAR TAREFA ---
        if "add" in request.POST:
            titulo = request.POST.get("titulo")
            descricao = request.POST.get("descricao")
            dificuldade = request.POST.get("dificuldade")

            if titulo.strip() != "":
                Tarefa.objects.create(
                    titulo=titulo,
                    descricao=descricao,
                    dificuldade=dificuldade,
                    usuario=request.user,
                    concluida=False,
                )

            return redirect('home')

        tarefa_id = request.POST.get("tarefa_id")
        tarefa = Tarefa.objects.get(id=tarefa_id, usuario=request.user)

        # --- CONCLUIR ---
        if "done" in request.POST:
            if not tarefa.concluida:
                tarefa.concluida = True
                tarefa.data_conclusao = timezone.now()
                tarefa.save()

                # adiciona XP
                ganho = PerfilUsuario.XP_BY_DIFFICULTY[tarefa.dificuldade]
                perfil.add_xp(ganho)

            return redirect('home')

        # --- EXCLUIR ---
        if "delete" in request.POST:
            tarefa.delete()
            return redirect('home')

        # --- RESTAURAR NA LIXEIRA ---
        if "restore" in request.POST:
            tarefa.concluida = False
            tarefa.save()
            return redirect('home')

    # =======================================================

    # Lê a aba da URL (?tab=ativas...)
    tab = request.GET.get("tab", "ativas")

    if tab == "ativas":
        tarefas = Tarefa.objects.filter(usuario=request.user, concluida=False)
    elif tab == "concluidas":
        tarefas = Tarefa.objects.filter(usuario=request.user, concluida=True)
    else:
        tarefas = []  # você ainda não implementou lixeira real

    # XP
    xp_needed = PerfilUsuario.xp_needed_for_level(perfil.level)
    xp_to_next = xp_needed - perfil.xp

    contexto = {
        "tarefas": tarefas,
        "tab": tab,
        "xp": perfil.xp,
        "level": perfil.level,
        "xp_needed_for_level": xp_needed,
        "xp_to_next": xp_to_next,
    }

    return render(request, 'home.html', contexto)


def logout_view(request):
    logout(request)
    return redirect('login')
