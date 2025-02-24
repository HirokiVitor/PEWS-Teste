from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PacienteViewSet, AvaliacaoViewSet, home, cadastrar_paciente, perfil_paciente, adicionar_pews, segunda_etapa_pews, historico_avaliacoes, login_user, logout_user, perfil_usuario, cadastrar_funcionario, remover_avaliacao, historico_pacientes, dar_alta_paciente

router = DefaultRouter()
router.register(r'pacientes', PacienteViewSet)
router.register(r'avaliacoes', AvaliacaoViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('', home, name='home'),
    path("cadastrar_paciente/", cadastrar_paciente, name="cadastrar_paciente"),
    path("paciente/<int:paciente_id>/", perfil_paciente, name="perfil_paciente"),
    path("paciente/<int:paciente_id>/adicionar_pews/", adicionar_pews, name="adicionar_pews"),
    path("paciente/<int:paciente_id>/segunda_etapa_pews/", segunda_etapa_pews, name="segunda_etapa_pews"),
    path("paciente/<int:paciente_id>/historico/", historico_avaliacoes, name="historico_avaliacoes"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("perfil/", perfil_usuario, name="perfil_usuario"),
    path("cadastrar_funcionario/", cadastrar_funcionario, name="cadastrar_funcionario"),
    path("remover_avaliacao/<int:avaliacao_id>/", remover_avaliacao, name="remover_avaliacao"),
    path("dar_alta/<int:paciente_id>/", dar_alta_paciente, name="dar_alta_paciente"),
    path("historico_pacientes/", historico_pacientes, name="historico_pacientes"),
]
