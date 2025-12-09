from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Tarefa, PerfilUsuario
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse


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

        PerfilUsuario.objects.create(usuario=user)

        login(request, user)
        return redirect('home')

    return render(request, 'register.html')


@login_required
def home(request):

    perfil, created = PerfilUsuario.objects.get_or_create(usuario=request.user)

    if request.method == "POST":

        # ADICIONAR TAREFA
        if "add" in request.POST:
            titulo = request.POST.get("titulo", "").strip()
            descricao = request.POST.get("descricao", "")
            dificuldade = request.POST.get("dificuldade", "M")

            if titulo != "":
                Tarefa.objects.create(
                    titulo=titulo,
                    descricao=descricao,
                    dificuldade=dificuldade,
                    usuario=request.user,
                    concluida=False,
                    lixeira=False
                )

            return redirect(reverse('home'))

        # pega tarefa_id com checagem
        tarefa_id = request.POST.get("tarefa_id")
        if not tarefa_id:
            return redirect(reverse('home'))

        try:
            tarefa = Tarefa.objects.get(id=tarefa_id, usuario=request.user)
        except Tarefa.DoesNotExist:
            return redirect(reverse('home'))

        # CONCLUIR
        if "done" in request.POST:
            if not tarefa.concluida:
                tarefa.concluida = True
                tarefa.data_conclusao = timezone.now()
                tarefa.save()

                ganho = PerfilUsuario.XP_BY_DIFFICULTY.get(tarefa.dificuldade, 0)
                perfil.add_xp(ganho)

            return redirect(reverse('home'))

        # ENVIAR PARA A LIXEIRA (soft delete)
        if "delete" in request.POST:
            tarefa.lixeira = True
            tarefa.concluida = False
            tarefa.save()
            return redirect(reverse('home') + '?tab=lixeira')

        # EXCLUIR DEFINITIVO (força apagar)
        if "force_delete" in request.POST:     # <-- AQUI É A ÚNICA ALTERAÇÃO
            if tarefa.lixeira:
                tarefa.delete()
            return redirect(reverse('home') + '?tab=lixeira')

        # RESTAURAR DA LIXEIRA
        if "restore" in request.POST:
            tarefa.lixeira = False
            tarefa.concluida = False
            tarefa.save()
            return redirect(reverse('home') + '?tab=ativas')

    # ========= FILTRO DAS ABAS =========
    tab = request.GET.get("tab", "ativas")

    if tab == "ativas":
        tarefas = Tarefa.objects.filter(usuario=request.user, concluida=False, lixeira=False)

    elif tab == "concluidas":
        tarefas = Tarefa.objects.filter(usuario=request.user, concluida=True, lixeira=False)

    elif tab == "lixeira":
        tarefas = Tarefa.objects.filter(usuario=request.user, lixeira=True)

    else:
        tarefas = []

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
