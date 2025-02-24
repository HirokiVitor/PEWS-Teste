from rest_framework import serializers
from .models import Paciente, Avaliacao

class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = '__all__'

class AvaliacaoSerializer(serializers.ModelSerializer):
    paciente = serializers.PrimaryKeyRelatedField(queryset=Paciente.objects.all())  # Corrige FK

    class Meta:
        model = Avaliacao
        fields = '__all__'
