from django.db import models
from django.contrib.auth.models import User

class Tarefa(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    concluida = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)


    class Meta:
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"
        
    def __str__(self):
        return self.titulo


class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    xp = models.IntegerField(default=0)
    dias_consecutivos = models.IntegerField(default=0)
    ultima_conclusao = models.DateField(null=True, blank=True)


    class Meta:
        verbose_name = "Perfil do Usuário"
        verbose_name_plural = "Perfis de Usuários"

    def __str__(self):
        return self.usuario.username
