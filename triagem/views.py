from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Paciente, Avaliacao
from .serializers import PacienteSerializer, AvaliacaoSerializer
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from triagem.models import Avaliacao, Paciente

def is_admin(user):
    return user.groups.filter(name="Administrador").exists() or user.is_superuser

@login_required
@user_passes_test(is_admin)
def dar_alta_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    paciente.ativo = False  # Marca o paciente como "de alta"
    paciente.save()
    messages.success(request, f"{paciente.nome} recebeu alta com sucesso!")
    return redirect("home")

@login_required
@user_passes_test(is_admin)
def historico_pacientes(request):
    pacientes = Paciente.objects.filter(ativo=False)  # Busca pacientes que receberam alta
    return render(request, "triagem/historico_pacientes.html", {"pacientes": pacientes})


@login_required
@user_passes_test(is_admin)
def remover_avaliacao(request, avaliacao_id):
    avaliacao = Avaliacao.objects.get(id=avaliacao_id)
    avaliacao.delete()
    messages.success(request, "Avaliação removida com sucesso!")
    return redirect("home")


# Verifica se o usuário pertence ao grupo Administrador

# View para cadastrar um novo funcionário (Apenas Administradores)
@login_required
@user_passes_test(is_admin)
def cadastrar_funcionario(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Usuário já existe.")
        else:
            user = User.objects.create_user(username=username, password=password)
            user.save()
            messages.success(request, "Funcionário cadastrado com sucesso!")
            return redirect("home")

    return render(request, "triagem/cadastrar_funcionario.html")

@login_required
def perfil_usuario(request):
    return render(request, "triagem/perfil_usuario.html")

# Tela de Login
def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login realizado com sucesso!")
            return redirect("home")  # Redireciona para a home ou outra página
        else:
            messages.error(request, "Usuário ou senha inválidos.")

    return render(request, "triagem/login.html")

# Logout
def logout_user(request):
    logout(request)
    messages.success(request, "Logout realizado com sucesso.")
    return redirect("login")

@login_required
def historico_avaliacoes(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)

    # Pega os parâmetros de filtro da URL
    filtro = request.GET.get("filtro", "data")  # Opções: 'data' ou 'score'
    ordem = request.GET.get("ordem", "desc")  # Opções: 'asc' (crescente) ou 'desc' (decrescente)

    # Define a ordenação correta
    if filtro == "score":
        ordenacao = "score" if ordem == "asc" else "-score"
    else:
        ordenacao = "data" if ordem == "asc" else "-data"  # Aqui estava errado

    # Busca todas as avaliações do paciente, ordenadas conforme o filtro
    avaliacoes = Avaliacao.objects.filter(paciente=paciente).order_by(ordenacao)

    context = {
        "paciente": paciente,
        "avaliacoes": avaliacoes,
        "filtro_selecionado": filtro,
        "ordem_selecionada": ordem,
    }
    return render(request, "triagem/historico_avaliacoes.html", context)

@login_required
def calcular_score(freq_cardiaca, freq_respiratoria, estado_crianca):
    score = 0
    
    # Avaliação da frequência cardíaca
    if freq_cardiaca < 60 or freq_cardiaca > 160:
        score += 2
    elif 60 <= freq_cardiaca <= 90 or 140 <= freq_cardiaca <= 160:
        score += 1
    
    # Avaliação da frequência respiratória
    if freq_respiratoria < 20 or freq_respiratoria > 60:
        score += 2
    elif 20 <= freq_respiratoria <= 30 or 50 <= freq_respiratoria <= 60:
        score += 1

    # Estado neurológico
    if estado_crianca == "Dormindo":
        score += 1

    return score

@login_required
def segunda_etapa_pews(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)

    # Recuperar dados da primeira etapa
    freq_cardiaca = request.session.get("freq_cardiaca", "")
    freq_respiratoria = request.session.get("freq_respiratoria", "")
    estado_crianca = request.session.get("estado_crianca", "")

    if request.method == "POST":
        av_neuro = request.POST.get("av_neuro")  # Agora sempre pegamos esse valor
        av_cardio = request.POST.get("av_cardio")
        av_resp = request.POST.get("av_resp")
        extras = request.POST.getlist("extras")  # Lista de checkboxes selecionados

        # Verifica se os valores estão preenchidos corretamente
        if not av_neuro or not av_cardio or not av_resp:
            messages.error(request, "Todos os campos da avaliação devem ser preenchidos!")
            return redirect("segunda_etapa_pews", paciente_id=paciente.id)

        # Calculando o score PEWS
        score = int(av_neuro) + int(av_cardio) + int(av_resp) + (2 * len(extras))

        # Criar a avaliação no banco de dados
        Avaliacao.objects.create(
            paciente=paciente,
            score=score,
            freq_cardiaca=freq_cardiaca,
            freq_respiratoria=freq_respiratoria,
            av_neuro=av_neuro,
            av_cardio=av_cardio,
            av_resp=av_resp,
            extras=", ".join(extras),
        )

        # Limpar sessão
        del request.session["freq_cardiaca"]
        del request.session["freq_respiratoria"]
        del request.session["estado_crianca"]

        messages.success(request, f"Avaliação PEWS adicionada com sucesso! Score: {score}")
        return redirect("perfil_paciente", paciente_id=paciente.id)

    return render(request, "triagem/segunda_etapa_pews.html", {
        "paciente": paciente,
        "freq_cardiaca": freq_cardiaca,
        "freq_respiratoria": freq_respiratoria,
        "estado_crianca": estado_crianca,
    })

@login_required
def adicionar_pews(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)

    if request.method == "POST":
        freq_cardiaca = request.POST.get("freq_cardiaca")
        freq_respiratoria = request.POST.get("freq_respiratoria")
        estado_crianca = request.POST.get("estado_crianca")

        if freq_cardiaca and freq_respiratoria and estado_crianca:
            # Salvamos os dados iniciais e seguimos para a próxima etapa
            request.session["freq_cardiaca"] = freq_cardiaca
            request.session["freq_respiratoria"] = freq_respiratoria
            request.session["estado_crianca"] = estado_crianca
            
            return redirect("segunda_etapa_pews", paciente_id=paciente.id)  # Redireciona para a próxima etapa

    return render(request, "triagem/adicionar_pews.html", {"paciente": paciente})

@login_required
def perfil_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)

    # Ordenar avaliações pela data mais recente e ID mais alto
    avaliacoes = Avaliacao.objects.filter(paciente=paciente).order_by("-data", "-id")

    # Obtém a última avaliação PEWS do paciente
    ultima_avaliacao = avaliacoes.first()

    # Preparar dados para o gráfico
    labels = [avaliacao.data.strftime("%d/%m") for avaliacao in avaliacoes]
    scores = [avaliacao.score for avaliacao in avaliacoes]

    context = {
        "paciente": paciente,
        "avaliacoes": avaliacoes,
        "ultima_avaliacao": ultima_avaliacao,  # Pegamos corretamente a última avaliação
        "labels": labels,
        "scores": scores,
    }
    return render(request, "triagem/perfil_paciente.html", context)

@login_required
def cadastrar_paciente(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        data_internacao = request.POST.get("data_internacao")
        leito = request.POST.get("leito")
        dih = request.POST.get("dih")
        diagnostico = request.POST.get("diagnostico")

        if nome and data_internacao and leito and dih and diagnostico:
            Paciente.objects.create(
                nome=nome,
                idade=0,  # Se precisar de um campo idade, ajuste isso
                leito=leito,
                dih=dih,
                diagnostico=diagnostico,
                data_internacao=data_internacao,
            )
            messages.success(request, "Paciente cadastrado com sucesso!")
            return redirect("home")  # Redireciona para a lista de pacientes

    return render(request, "triagem/cadastrar_paciente.html")

@login_required
def home(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Redireciona para a página de login se não estiver logado

    pacientes = Paciente.objects.filter(ativo=True)
    return render(request, "triagem/home.html", {"pacientes": pacientes})  # Caso contrário, exibe a página inicial



class PacienteViewSet(viewsets.ModelViewSet):
    """CRUD para Pacientes"""
    queryset = Paciente.objects.all().order_by('-created_at')
    serializer_class = PacienteSerializer
    permission_classes = [IsAuthenticated]

class AvaliacaoViewSet(viewsets.ModelViewSet):
    """CRUD para Avaliações"""
    queryset = Avaliacao.objects.all().order_by('-data')
    serializer_class = AvaliacaoSerializer
    permission_classes = [IsAuthenticated]
