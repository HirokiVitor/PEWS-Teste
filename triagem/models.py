from django.contrib.auth.models import User
from django.db import models

class Paciente(models.Model):
    nome = models.CharField(max_length=100)
    idade = models.IntegerField()
    leito = models.CharField(max_length=20)
    dih = models.CharField(max_length=50)
    diagnostico = models.TextField()
    data_internacao = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class Avaliacao(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='avaliacoes')
    data = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField()
    intervencao = models.TextField(blank=True, null=True)
    freq_cardiaca = models.IntegerField()
    freq_respiratoria = models.IntegerField()
    av_neuro = models.TextField()
    av_cardio = models.TextField()
    av_resp = models.TextField()
    extras = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Avaliação de {self.paciente.nome} em {self.data.strftime('%d/%m/%Y %H:%M')}"


