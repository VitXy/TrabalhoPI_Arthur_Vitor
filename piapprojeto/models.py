from django.db import models
from django.contrib.auth.models import User
<<<<<<< HEAD
from django.utils import timezone
import math
=======
>>>>>>> cbff90f (Atualizando branch vitor)

class Tarefa(models.Model):
    DIFICULDADE_CHOICES = [
        ('F', 'Fácil'),
        ('M', 'Média'),
        ('D', 'Difícil'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    dificuldade = models.CharField(max_length=1, choices=DIFICULDADE_CHOICES, default='M')

    concluida = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)

<<<<<<< HEAD
    # SOFT DELETE
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

=======

    class Meta:
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"
        
>>>>>>> cbff90f (Atualizando branch vitor)
    def __str__(self):
        return f"{self.titulo} ({self.get_dificuldade_display()})"


class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)

    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)

    dias_consecutivos = models.IntegerField(default=0)
    ultima_conclusao = models.DateField(null=True, blank=True)


    class Meta:
        verbose_name = "Perfil do Usuário"
        verbose_name_plural = "Perfis de Usuários"

    def __str__(self):
        return self.usuario.username

    XP_BY_DIFFICULTY = {
        'F': 10,
        'M': 20,
        'D': 40,
    }

    @staticmethod
    def xp_needed_for_level(level):
        return int(100 * (level ** 1.5))

    def add_xp(self, amount):
        old_level = self.level
        self.xp += amount

        leveled_up = False
        while self.xp >= self.xp_needed_for_level(self.level):
            self.level += 1
            leveled_up = True

        self.save()

        return {
            "xp": self.xp,
            "level": self.level,
            "leveled_up": leveled_up,
        }
