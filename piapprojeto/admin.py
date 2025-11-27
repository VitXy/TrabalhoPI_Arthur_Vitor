from django.contrib import admin
from .models import Tarefa, PerfilUsuario


@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "usuario", "concluida", "data_criacao", "data_conclusao")
    list_filter = ("concluida", "data_criacao")
    search_fields = ("titulo", "descricao")
    ordering = ("-data_criacao",)

    fieldsets = (
        ("Informações da Tarefa", {
            "fields": ("usuario", "titulo", "descricao")
        }),
        ("Status", {
            "fields": ("concluida",),
        }),
    )


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "xp", "dias_consecutivos", "ultima_conclusao")
    search_fields = ("usuario__username",)
    ordering = ("-xp",)
