# secretaria/views.py
from typing import Optional

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User, Group
# [CORREÇÃO] Adicionando 'models' para referências de query
from django.db import transaction, models
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
# [CORREÇÃO] Adicionando 'timezone' para 'data__gte'
from django.utils import timezone
from django.utils.text import slugify
import uuid
import random
import string

from rest_framework_simplejwt.views import TokenObtainPairView

from .permissions import (
    IsSecretaria, IsProfessor, IsResponsavel, IsAluno, IsAuxiliarAdmin,
    IsOwnerOrReadOnly, IsAlunoOwner, IsResponsavelRelated
)
from .models import (
    Responsavel, Aluno, Professor, Bimestre, Nota, AtividadePendente,
    EventoExtracurricular, Advertencia, Suspensao, PlanejamentoSemanal,
    EventoCalendario, EmprestimoLivro, Livro, PasswordResetToken, Sala, Reserva
)
from .serializers import (
    ResponsavelSerializer, AlunoSerializer, ProfessorSerializer, BimestreSerializer,
    NotaSerializer, AtividadePendenteSerializer, EventoExtracurricularSerializer,
    AdvertenciaSerializer, SuspensaoSerializer, PlanejamentoSemanalSerializer,
    EventoCalendarioSerializer, EmprestimoLivroSerializer, LivroSerializer,
    SalaSerializer, ReservaSerializer, MyTokenObtainPairSerializer
)

# Funções auxiliares
def get_professor_by_user(user):
    """Tenta obter o objeto Professor associado ao usuário logado."""
    try:
        return Professor.objects.get(user=user)
    except Professor.DoesNotExist:
        return None

def get_aluno_by_user(user):
    """Tenta obter o objeto Aluno associado ao usuário logado."""
    try:
        return Aluno.objects.get(user=user)
    except Aluno.DoesNotExist:
        return None

def get_responsavel_by_user(user):
    """Tenta obter o objeto Responsavel associado ao usuário logado."""
    try:
        return Responsavel.objects.get(user=user)
    except Responsavel.DoesNotExist:
        return None

def get_alunos_do_responsavel(user):
    """Retorna todos os alunos associados a um responsável."""
    try:
        responsavel = Responsavel.objects.get(user=user)
        return Aluno.objects.filter(Responsavel=responsavel)
    except Responsavel.DoesNotExist:
        return Aluno.objects.none()

# =================================================================
# --- [NOVA FUNÇÃO] Verifica se usuário tem cargo de Professor ---
# =================================================================
def user_has_professor_cargo(user):
    """
    Verifica se o usuário tem cargo 'Professor' baseado no token JWT
    Esta função assume que o cargo está disponível no objeto user
    através do token JWT customizado
    """
    return hasattr(user, 'cargo') and user.cargo == 'Professor'

# =================================================================
# --- [FUNÇÃO MODIFICADA] get_professor_by_user melhorada ---
# =================================================================
def get_professor_by_user_enhanced(user):
    """
    Tenta encontrar o perfil de Professor vinculado ao usuário
    Retorna o objeto Professor ou None se não encontrado
    """
    if not user or not user.is_authenticated:
        return None
    
    try:
        # 1. Tenta pelo relacionamento direto (OneToOneField)
        if hasattr(user, 'professor'):
            return user.professor
    except Professor.DoesNotExist:
        pass
    
    try:
        # 2. Tenta buscar pelo user_id (ForeignKey)
        return Professor.objects.get(user=user)
    except Professor.DoesNotExist:
        pass
    
    try:
        # 3. Tenta pelo ID do usuário (se o ID do professor for o mesmo)
        return Professor.objects.get(id=user.id)
    except (Professor.DoesNotExist, ValueError):
        pass
    
    # 4. Tenta pelo email (caso o email do professor seja o mesmo do usuário)
    if user.email:
        try:
            return Professor.objects.get(email_professor__iexact=user.email)
        except (Professor.DoesNotExist, Professor.MultipleObjectsReturned):
            pass
    
    return None

# Funções de views HTML
def calendario_academico(request):
    eventos = EventoCalendario.objects.order_by('data')
    return render(request, 'calendario.html', {'eventos': eventos})

def media_aluno_disciplina(request, aluno_id, disciplina):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    media = aluno.media_por_disciplina(disciplina)
    return render(request, 'media_aluno.html', {
        'aluno': aluno,
        'disciplina': disciplina,
        'media': media,
    })

# ViewSets de CRUD Total (Apenas para a Secretaria)
class ResponsavelViewSet(viewsets.ModelViewSet):
    queryset = Responsavel.objects.all()
    serializer_class = ResponsavelSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsSecretaria]
        elif self.action in ['retrieve']:
            # Responsável pode ver apenas seu próprio perfil
            self.permission_classes = [IsSecretaria | IsResponsavel]
        else:
            self.permission_classes = [IsSecretaria]
        return super().get_permissions()
    
    def get_queryset(self):
        user = self.request.user
        if IsResponsavel().has_permission(self.request, self):
            return Responsavel.objects.filter(user=user)
        return Responsavel.objects.all()

class ProfessorViewSet(viewsets.ModelViewSet):
    queryset = Professor.objects.all()
    serializer_class = ProfessorSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsSecretaria]
        elif self.action in ['retrieve']:
            # Professor pode ver apenas seu próprio perfil
            self.permission_classes = [IsSecretaria | IsProfessor]
        else:
            self.permission_classes = [IsSecretaria]
        return super().get_permissions()
    
    def get_queryset(self):
        user = self.request.user
        if IsProfessor().has_permission(self.request, self):
            return Professor.objects.filter(user=user)
        return Professor.objects.all()

# =================================================================
# --- [ALTERAÇÕES] AlunoViewSet ---
# =================================================================
class AlunoViewSet(viewsets.ModelViewSet):
    queryset = Aluno.objects.all()
    serializer_class = AlunoSerializer
    
    def get_permissions(self):
        # --- [REGRA] Professor: Permite Leitura (filtrada)
        # --- [REGRA] Auxiliar: Permite Leitura (total) e Update (limitado)
        if self.action in ['create', 'destroy']:
            self.permission_classes = [IsSecretaria]
        
        elif self.action in ['update', 'partial_update']:
            # Permite Secretaria (total), Professor (comentários), Auxiliar (faltas)
            self.permission_classes = [IsSecretaria | IsProfessor | IsAuxiliarAdmin]
        
        elif self.action in ['list', 'retrieve']:
            self.permission_classes = [IsSecretaria | IsAluno | IsResponsavel | IsAuxiliarAdmin | IsProfessor]
        
        else:
            self.permission_classes = [IsSecretaria | IsAuxiliarAdmin]
        
        return super().get_permissions()
    
    def get_queryset(self):
        user = self.request.user

        # --- [REGRA] Professor: Filtra alunos pelas turmas do PlanejamentoSemanal
        if IsProfessor().has_permission(self.request, self):
            professor = get_professor_by_user(user)
            if professor:
                # 1. Encontra as turmas (class_choice) que o professor leciona
                turmas_do_professor = PlanejamentoSemanal.objects.filter(
                    professor=professor
                ).values_list('turma', flat=True).distinct()
                
                # 2. Retorna apenas alunos dessas turmas
                return Aluno.objects.filter(class_choice__in=turmas_do_professor)
            return Aluno.objects.none() # Professor sem perfil não vê ninguém
        
        # --- [REGRA] Aluno: Vê apenas a si mesmo
        if IsAluno().has_permission(self.request, self):
            return Aluno.objects.filter(user=user)
        
        # --- [REGRA] Responsável: Vê apenas seus alunos
        elif IsResponsavel().has_permission(self.request, self):
            return get_alunos_do_responsavel(user)
        
        # --- [REGRA] Secretaria/Auxiliar: Vê todos
        # (A permissão de 'list' já foi verificada em get_permissions)
        return Aluno.objects.all()

    # --- [NOVO MÉTODO] Sobrescreve 'update' (PUT) e 'partial_update' (PATCH)
    def update(self, request, *args, **kwargs):
        user = request.user
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance) # Pega o serializer com dados atuais
        cleaned_data = {} # Dicionário para os dados "limpos"
        
        # --- [REGRA] Auxiliar: Só pode editar Faltas e Presenças
        if IsAuxiliarAdmin().has_permission(request, self):
            allowed_fields = ['faltas_aluno', 'presencas_aluno']
            
            # Se for PATCH (partial=True), só permitimos os campos da lista
            if partial:
                for field in allowed_fields:
                    if field in request.data:
                        cleaned_data[field] = request.data[field]
                
                # Checa se tentou editar campos não permitidos
                for field in request.data:
                     if field not in allowed_fields:
                        raise PermissionDenied(f'Auxiliares não podem editar o campo: {field}.')
                
                if not cleaned_data:
                    # Não enviou nada ou enviou campos vazios
                    return Response(serializer.data) # Retorna dados atuais sem erro

                serializer_data = cleaned_data
            
            else: # Se for PUT (partial=False)
                # Pega os dados atuais
                serializer_data = serializer.data
                # Atualiza apenas os campos permitidos com os dados da requisição
                serializer_data.update({
                    'faltas_aluno': request.data.get('faltas_aluno', instance.faltas_aluno),
                    'presencas_aluno': request.data.get('presencas_aluno', instance.presencas_aluno)
                })
        
        # --- [REGRA] Professor: Só pode editar 'comentario_descritivo'
        elif IsProfessor().has_permission(request, self):
            if 'comentario_descritivo' in request.data:
                cleaned_data['comentario_descritivo'] = request.data['comentario_descritivo']
            
            if partial:
                # Checa se tentou editar campos não permitidos
                for field in request.data:
                     if field != 'comentario_descritivo':
                        raise PermissionDenied(f'Professores não podem editar o campo: {field}.')
                
                if not cleaned_data:
                     return Response(serializer.data) # Retorna dados atuais
                
                serializer_data = cleaned_data
            
            else: # Se for PUT
                serializer_data = serializer.data
                serializer_data.update({
                    'comentario_descritivo': request.data.get('comentario_descritivo', instance.comentario_descritivo)
                })

        # --- [REGRA] Secretaria: Acesso total (usa os dados originais)
        else: 
            serializer_data = request.data
        
        # Recria o serializer com os dados limpos
        serializer = self.get_serializer(instance, data=serializer_data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


# =================================================================
# --- [ALTERAÇÕES] NotaViewSet ---
# =================================================================
class NotaViewSet(viewsets.ModelViewSet):
    queryset = Nota.objects.all()
    serializer_class = NotaSerializer

    def get_queryset(self):
        user = self.request.user
        
        # --- [REGRA] Professor: Filtra notas pelas turmas e disciplina do professor
        if IsProfessor().has_permission(self.request, self):
            professor = get_professor_by_user(user)
            if professor:
                # 1. Encontra as turmas (class_choice) que o professor leciona
                turmas_do_professor = PlanejamentoSemanal.objects.filter(
                    professor=professor
                ).values_list('turma', flat=True).distinct()
                
                # 2. Encontra os alunos dessas turmas
                alunos_das_turmas = Aluno.objects.filter(class_choice__in=turmas_do_professor)
                
                # 3. Retorna notas desses alunos E da disciplina do professor
                return Nota.objects.filter(
                    aluno__in=alunos_das_turmas,
                    disciplina=professor.disciplina
                )
            return Nota.objects.none() # Professor sem perfil não vê nada

        # --- [REGRA] Secretaria: Vê tudo
        if IsSecretaria().has_permission(self.request, self):
            return Nota.objects.all()
        
        # --- [REGRA] Responsável: Vê notas dos seus alunos
        elif IsResponsavel().has_permission(self.request, self):
            alunos = get_alunos_do_responsavel(user)
            return Nota.objects.filter(aluno__in=alunos)
        
        # --- [REGRA] Aluno: Vê apenas suas notas
        elif IsAluno().has_permission(self.request, self):
            aluno = get_aluno_by_user(user)
            if aluno:
                return Nota.objects.filter(aluno=aluno)
        
        return Nota.objects.none()

    def get_permissions(self):
        # Apenas Secretaria e Professor podem criar/editar/excluir notas
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsSecretaria | IsProfessor]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    # --- [NOVO MÉTODO] Garante que o professor só edite notas da sua própria disciplina
    def perform_update(self, serializer):
        user = self.request.user
        
        # --- [REGRA] Professor: Validação de Disciplina
        if IsProfessor().has_permission(self.request, self):
            professor = get_professor_by_user(user)
            nota = serializer.instance # A nota que está sendo editada
            
            # Checa se a disciplina da nota é a mesma do professor
            if professor and nota.disciplina != professor.disciplina:
                raise PermissionDenied('Você só pode editar notas da sua disciplina principal.')
            
            # Checa se o 'novo' valor da disciplina (se enviado) é o do professor
            if 'disciplina' in serializer.validated_data and serializer.validated_data['disciplina'] != professor.disciplina:
                raise PermissionDenied('Você não pode alterar a disciplina para uma que não seja a sua.')

        serializer.save()

    # --- [NOVO MÉTODO] Garante que o professor só crie notas da sua própria disciplina
    def perform_create(self, serializer):
        user = self.request.user

        # --- [REGRA] Professor: Validação de Disciplina
        if IsProfessor().has_permission(self.request, self):
            professor = get_professor_by_user(user)
            
            # Se o professor tentou enviar uma disciplina diferente da sua
            if 'disciplina' in serializer.validated_data and serializer.validated_data['disciplina'] != professor.disciplina:
                raise PermissionDenied('Você só pode criar notas para a sua disciplina principal.')
            
            # Força a disciplina do professor no payload
            serializer.save(disciplina=professor.disciplina)
        else:
            serializer.save()

# --- AtividadePendenteViewSet (Sem alterações) ---
class AtividadePendenteViewSet(viewsets.ModelViewSet):
    queryset = AtividadePendente.objects.all()
    serializer_class = AtividadePendenteSerializer

    def get_queryset(self):
        user = self.request.user
        # Secretaria e Professor veem todas as tarefas
        if IsSecretaria().has_permission(self.request, self) or IsProfessor().has_permission(self.request, self):
            return AtividadePendente.objects.all()
        # Responsável ve apenas tarefas dos seus alunos
        elif IsResponsavel().has_permission(self.request, self):
            alunos = get_alunos_do_responsavel(user)
            return AtividadePendente.objects.filter(aluno__in=alunos)
        # Aluno ve apenas suas próprias tarefas
        elif IsAluno().has_permission(self.request, self):
            aluno = get_aluno_by_user(user)
            if aluno:
                return AtividadePendente.objects.filter(aluno=aluno)
        return AtividadePendente.objects.none()

    def get_permissions(self):
        # Apenas Secretaria e Professor podem criar/editar tarefas
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsSecretaria | IsProfessor]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()


# =================================================================
# --- [ALTERAÇÕES PRINCIPAIS] PlanejamentoSemanalViewSet ---
# =================================================================
class PlanejamentoSemanalViewSet(viewsets.ModelViewSet):
    queryset = PlanejamentoSemanal.objects.all()
    serializer_class = PlanejamentoSemanalSerializer

    def get_permissions(self):
        # Apenas Secretaria e Professor podem gerenciar planejamentos
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsSecretaria | IsProfessor]
        else:
            # Todos autenticados podem ver os planejamentos
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    # --- [NOVO MÉTODO] Filtra para que o professor veja apenas os seus
    def get_queryset(self):
        user = self.request.user
        
        # --- [REGRA] Professor: Vê apenas os seus
        if IsProfessor().has_permission(self.request, self) or user_has_professor_cargo(user):
            professor = get_professor_by_user_enhanced(user)
            if professor:
                return PlanejamentoSemanal.objects.filter(professor=professor)
            return PlanejamentoSemanal.objects.none()
        
        # --- [REGRA] Secretaria: Vê todos
        if IsSecretaria().has_permission(self.request, self):
            return PlanejamentoSemanal.objects.all()
        
        # --- [REGRA] Alunos/Responsáveis: Vêem todos
        if IsAluno().has_permission(self.request, self) or IsResponsavel().has_permission(self.request, self):
            return PlanejamentoSemanal.objects.all()

        return PlanejamentoSemanal.objects.none()

    # --- [NOVO MÉTODO] Garante que o professor só crie para si mesmo
    def perform_create(self, serializer):
        user = self.request.user
        
        # --- [REGRA] Professor: Força o 'professor' a ser o usuário logado
        if IsProfessor().has_permission(self.request, self) or user_has_professor_cargo(user):
            professor = get_professor_by_user_enhanced(user)
            if not professor:
                raise PermissionDenied(
                    "Seu usuário tem cargo de Professor, mas não possui um perfil de Professor vinculado. "
                    "Contate a secretaria para vincular seu usuário a um perfil de Professor."
                )
            
            # Impede que o professor se passe por outro
            if 'professor' in serializer.validated_data and serializer.validated_data['professor'] != professor:
                raise PermissionDenied('Você só pode criar planejamentos para si mesmo.')
            
            serializer.save(professor=professor)
        else:
            # Secretaria pode definir qualquer professor
            serializer.save()

    # --- [NOVO MÉTODO] Garante que o professor só edite seus próprios planejamentos
    def perform_update(self, serializer):
        user = self.request.user
        
        # --- [REGRA] Professor: Checa se é o dono do planejamento
        if IsProfessor().has_permission(self.request, self) or user_has_professor_cargo(user):
            professor = get_professor_by_user_enhanced(user)
            if not professor:
                raise PermissionDenied("Perfil de Professor não encontrado para este usuário.")
            
            # Checa se ele é o dono do planejamento que está tentando editar
            if serializer.instance.professor != professor:
                raise PermissionDenied('Você não pode editar o planejamento de outro professor.')
            
            # Impede que ele troque o dono
            if 'professor' in serializer.validated_data and serializer.validated_data['professor'] != professor:
                raise PermissionDenied('Você não pode transferir o planejamento para outro professor.')

        serializer.save()


# --- planejamento_opcoes (Sem alterações) ---
@api_view(['GET'])
def planejamento_opcoes(request):
    opcoes = {    
        'turnos': [
            {'value': 'MANHA', 'label': 'Manhã'},
            {'value': 'TARDE', 'label': 'Tarde'}, 
            {'value': 'NOITE', 'label': 'Noite'},
        ],
        'turmas': [
            {'value': '1A', 'label': '1 ANO A'},
            {'value': '1B', 'label': '1 ANO B'},
            {'value': '1C', 'label': '1 ANO C'},
            {'value': '2A', 'label': '2 ANO A'},
            {'value': '2B', 'label': '2 ANO B'},
            {'value': '2C', 'label': '2 ANO C'},
            {'value': '3A', 'label': '3 ANO A'},
            {'value': '3B', 'label': '3 ANO B'},
            {'value': '3C', 'label': '3 ANO C'},
        ]
    }
    return Response(opcoes)

# --- AdvertenciaViewSet (Sem alterações) ---
class AdvertenciaViewSet(viewsets.ModelViewSet):
    queryset = Advertencia.objects.all()
    serializer_class = AdvertenciaSerializer

    def get_queryset(self):
        user = self.request.user
        # Secretaria e Professor veem todas as advertências
        if IsSecretaria().has_permission(self.request, self) or IsProfessor().has_permission(self.request, self):
            return Advertencia.objects.all()
        # Responsável ve apenas advertências dos seus alunos
        elif IsResponsavel().has_permission(self.request, self):
            alunos = get_alunos_do_responsavel(user)
            return Advertencia.objects.filter(aluno__in=alunos)
        # Aluno ve apenas suas próprias advertências
        elif IsAluno().has_permission(self.request, self):
            aluno = get_aluno_by_user(user)
            if aluno:
                return Advertencia.objects.filter(aluno=aluno)
        return Advertencia.objects.none()

    def get_permissions(self):
        # Apenas Secretaria pode criar/editar advertências
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsSecretaria]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

# --- SuspensaoViewSet (Sem alterações) ---
class SuspensaoViewSet(viewsets.ModelViewSet):
    queryset = Suspensao.objects.all()
    serializer_class = SuspensaoSerializer

    def get_queryset(self):
        user = self.request.user
        # Secretaria e Professor veem todas as suspensões
        if IsSecretaria().has_permission(self.request, self) or IsProfessor().has_permission(self.request, self):
            return Suspensao.objects.all()
        # Responsável ve apenas suspensões dos seus alunos
        elif IsResponsavel().has_permission(self.request, self):
            alunos = get_alunos_do_responsavel(user)
            return Suspensao.objects.filter(aluno__in=alunos)
        # Aluno ve apenas suas próprias suspensões
        elif IsAluno().has_permission(self.request, self):
            aluno = get_aluno_by_user(user)
            if aluno:
                return Suspensao.objects.filter(aluno=aluno)
        return Suspensao.objects.none()

    def get_permissions(self):
        # Apenas Secretaria pode criar/editar suspensões
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsSecretaria]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

# --- EventoExtracurricularViewSet (Sem alterações) ---
class EventoExtracurricularViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EventoExtracurricular.objects.all()
    serializer_class = EventoExtracurricularSerializer
    permission_classes = [IsAuthenticated]

# =================================================================
# --- [ALTERAÇÕES] EventoCalendarioViewSet ---
# =================================================================
class EventoCalendarioViewSet(viewsets.ModelViewSet):
    queryset = EventoCalendario.objects.all()
    serializer_class = EventoCalendarioSerializer
    
    def get_permissions(self):
        # --- [REGRA] Auxiliar: Permite CRUD
        # --- [REGRA] Aluno/Responsável/Professor: Apenas Leitura
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsSecretaria | IsAuxiliarAdmin] # <-- ADICIONADO AUXILIAR
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

# --- LivroViewSet (Sem alterações, regra já correta) ---
class LivroViewSet(viewsets.ModelViewSet):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # --- [REGRA] Auxiliar: CRUD (Já estava correto)
            self.permission_classes = [IsAuxiliarAdmin]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

# --- EmprestimoLivroViewSet (Sem alterações, regra já correta) ---
class EmprestimoLivroViewSet(viewsets.ModelViewSet):
    serializer_class = EmprestimoLivroSerializer
    queryset = EmprestimoLivro.objects.all()
    
    def get_queryset(self):
        user = self.request.user
        
        # DEBUG: Verificar usuário e permissões
        print(f"Usuário: {user}, Tipo: {getattr(user, 'tipo', 'N/A')}")
        print(f"É staff: {user.is_staff}, É superuser: {user.is_superuser}")
        
        # SECRETARIA e AUXILIAR ADMIN têm acesso completo
        if IsAuxiliarAdmin().has_permission(self.request, self) or IsSecretaria().has_permission(self.request, self):
            print("Acesso completo: AuxiliarAdmin ou Secretaria")
            return EmprestimoLivro.objects.all().select_related('aluno', 'computador')
        
        # RESPONSÁVEL: vê apenas empréstimos dos seus alunos
        elif IsResponsavel().has_permission(self.request, self):
            print("Acesso responsável")
            from .utils import get_alunos_do_responsavel
            alunos = get_alunos_do_responsavel(user)
            return EmprestimoLivro.objects.filter(aluno__in=alunos).select_related('aluno', 'computador')
        
        # ALUNO: vê apenas seus próprios empréstimos
        elif IsAluno().has_permission(self.request, self):
            print("Acesso aluno")
            from .utils import get_aluno_by_user
            aluno = get_aluno_by_user(user)
            if aluno:
                return EmprestimoLivro.objects.filter(aluno=aluno).select_related('aluno', 'computador')
        
        print("Nenhuma permissão encontrada, retornando vazio")
        return EmprestimoLivro.objects.none()
    
    def get_permissions(self):
        """
        Define as permissões baseadas na ação
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # SECRETARIA e AUXILIAR ADMIN podem criar/editar/deletar
            self.permission_classes = [permissions.IsAuthenticated, (IsAuxiliarAdmin | IsSecretaria)]
        else:
            # Para list e retrieve, qualquer usuário autenticado pode ver (com filtros)
            self.permission_classes = [permissions.IsAuthenticated]
        
        return super().get_permissions()
    
    def create(self, request, *args, **kwargs):
        """
        Sobrescreve create para melhor tratamento de erros
        """
        try:
            print(f"Criando empréstimo para usuário: {request.user}")
            print(f"Dados recebidos: {request.data}")
            
            # Verificar permissão explicitamente
            if not (IsAuxiliarAdmin().has_permission(request, self) or IsSecretaria().has_permission(request, self)):
                return Response(
                    {"detail": "Você não tem permissão para criar empréstimos."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            return super().create(request, *args, **kwargs)
            
        except Exception as e:
            print(f"Erro ao criar empréstimo: {str(e)}")
            return Response(
                {"detail": f"Erro ao criar empréstimo: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """
        Sobrescreve update para melhor tratamento de erros
        """
        try:
            print(f"Atualizando empréstimo para usuário: {request.user}")
            
            # Verificar permissão explicitamente
            if not (IsAuxiliarAdmin().has_permission(request, self) or IsSecretaria().has_permission(request, self)):
                return Response(
                    {"detail": "Você não tem permissão para editar empréstimos."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            return super().update(request, *args, **kwargs)
            
        except Exception as e:
            print(f"Erro ao atualizar empréstimo: {str(e)}")
            return Response(
                {"detail": f"Erro ao atualizar empréstimo: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def partial_update(self, request, *args, **kwargs):
        """
        Sobrescreve partial_update para PATCH
        """
        try:
            print(f"Partial update empréstimo para usuário: {request.user}")
            
            # Verificar permissão explicitamente
            if not (IsAuxiliarAdmin().has_permission(request, self) or IsSecretaria().has_permission(request, self)):
                return Response(
                    {"detail": "Você não tem permissão para editar empréstimos."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            return super().partial_update(request, *args, **kwargs)
            
        except Exception as e:
            print(f"Erro no partial update: {str(e)}")
            return Response(
                {"detail": f"Erro ao atualizar empréstimo: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """
        Sobrescreve destroy para melhor tratamento
        """
        try:
            print(f"Deletando empréstimo para usuário: {request.user}")
            
            # Verificar permissão explicitamente
            if not (IsAuxiliarAdmin().has_permission(request, self) or IsSecretaria().has_permission(request, self)):
                return Response(
                    {"detail": "Você não tem permissão para deletar empréstimos."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            return super().destroy(request, *args, **kwargs)
            
        except Exception as e:
            print(f"Erro ao deletar empréstimo: {str(e)}")
            return Response(
                {"detail": f"Erro ao deletar empréstimo: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='devolver')
    def devolver(self, request, pk=None):
        """
        Ação customizada para registrar devolução
        """
        try:
            emprestimo = self.get_object()
            
            # Verificar permissão
            if not (IsAuxiliarAdmin().has_permission(request, self) or IsSecretaria().has_permission(request, self)):
                return Response(
                    {"detail": "Você não tem permissão para registrar devoluções."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Marcar como devolvido
            emprestimo.devolvido = True
            emprestimo.data_devolucao = timezone.now().date()
            emprestimo.save()
            
            serializer = self.get_serializer(emprestimo)
            return Response(serializer.data)
            
        except EmprestimoLivro.DoesNotExist:
            return Response(
                {"detail": "Empréstimo não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": f"Erro ao registrar devolução: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], url_path='pendentes')
    def pendentes(self, request):
        """
        Lista empréstimos pendentes (não devolvidos)
        """
        try:
            queryset = self.get_queryset().filter(devolvido=False)
            
            # Aplicar paginação se necessário
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {"detail": f"Erro ao buscar empréstimos pendentes: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def list(self, request, *args, **kwargs):
        """
        Sobrescreve list para debug
        """
        print(f"Listando empréstimos para usuário: {request.user}")
        queryset = self.get_queryset()
        print(f"Total de empréstimos encontrados: {queryset.count()}")
        
        return super().list(request, *args, **kwargs)

# --- BimestreViewSet (Sem alterações) ---
class BimestreViewSet(viewsets.ModelViewSet):
    queryset = Bimestre.objects.all()
    serializer_class = BimestreSerializer
    permission_classes = [IsSecretaria]

# --- SalaViewSet (Sem alterações) ---
class SalaViewSet(viewsets.ModelViewSet):
    queryset = Sala.objects.all()
    serializer_class = SalaSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsSecretaria]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

# =================================================================
# --- [ALTERAÇÕES] ReservaViewSet ---
# =================================================================
class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_anonymous:
            return Reserva.objects.none()

        # --- [REGRA] Secretaria: Vê todas as reservas
        if IsSecretaria().has_permission(self.request, self):
            return Reserva.objects.all()
        
        # --- [REGRA] Professor: Vê apenas as suas (ativas/futuras)
        if IsProfessor().has_permission(self.request, self) or user_has_professor_cargo(user):
            professor = get_professor_by_user_enhanced(user)
            if professor:
                # Filtra por data futura ou atual para o painel
                return Reserva.objects.filter(
                    professor=professor, 
                    data__gte=timezone.now().date()
                ) 
            
        return Reserva.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        
        # --- [REGRA] Professor: Apenas professor pode criar
        # (Secretaria é tratada em 'get_permissions')
        if IsProfessor().has_permission(self.request, self) or user_has_professor_cargo(user):
            professor = get_professor_by_user_enhanced(user)
            if not professor:
                raise PermissionDenied("Apenas Professores com perfil podem criar reservas.")
            
            # Força o professor a ser o usuário logado
            serializer.save(professor=professor) 
        else:
            # Secretaria pode criar em nome de outros (se 'professor' for enviado no payload)
            serializer.save()
            
    def get_permissions(self):
        # --- [REGRA] Professor: Pode Criar e Destruir (suas próprias)
        # --- [REGRA] Secretaria: CRUD Total
        if self.action in ['create', 'destroy']:
            self.permission_classes = [IsProfessor | IsSecretaria]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [IsSecretaria] # Professor não pode editar, só criar/excluir
        else: # list, retrieve
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

# --- UserRegistrationBySecretariaView (Sem alterações) ---
class UserRegistrationBySecretariaView(APIView):
    permission_classes = [IsSecretaria] 

    @transaction.atomic 
    def post(self, request):
        full_name = request.data.get('full_name')
        cpf = request.data.get('cpf')
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')
        cargo = request.data.get('cargo') # 'aluno', 'responsavel', 'professor'
        birthday = request.data.get('birthday')
        password = request.data.get('password')

        required_fields = [full_name, cpf, email, phone_number, cargo, birthday, password]
        if not all(required_fields):
            return Response({'error': 'Todos os campos são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Este e-mail já está em uso.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.create_user(username=cpf, email=email, password=password)
            user.first_name = full_name.split(' ')[0]
            user.last_name = ' '.join(full_name.split(' ')[1:])
            user.save()
        except Exception as e:
            return Response({'error': f'Erro ao criar usuário: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            if cargo.lower() == 'aluno':
                group = Group.objects.get(name='Aluno')
                Aluno.objects.create(
                    user=user, name_aluno=full_name, cpf_aluno=cpf, email_aluno=email, 
                    phone_number_aluno=phone_number, birthday_aluno=birthday
                    # Atenção: Faltarão outros campos obrigatórios de Aluno
                )
            elif cargo.lower() == 'responsavel':
                group = Group.objects.get(name='Responsavel')
                Responsavel.objects.create(
                    user=user, name=full_name, cpf=cpf, email=email, 
                    phone_number=phone_number, birthday=birthday
                )
            elif cargo.lower() == 'professor':
                group = Group.objects.get(name='Professor')
                Professor.objects.create(
                    user=user, name_professor=full_name, cpf_professor=cpf, email_professor=email,
                    phone_number_professor=phone_number, birthday_professor=birthday
                )
            else:
                user.delete() 
                return Response({'error': 'Cargo inválido.'}, status=status.HTTP_400_BAD_REQUEST)

            user.groups.add(group)
        except Group.DoesNotExist:
             return Response({'error': f'O grupo {cargo} não foi encontrado. Crie-o no painel admin.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': f'Erro ao criar perfil: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'success': f'Usuário {full_name} ({cargo}) criado com sucesso!'}, status=status.HTTP_201_CREATED)

# --- MyTokenObtainPairView (Sem alterações) ---
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

# --- PasswordReset Views (Sem alterações) ---
def _build_unique_username(base_value: str, fallback_prefix: str) -> str:
    base_slug = slugify(base_value) if base_value else ''
    if not base_slug:
        base_slug = fallback_prefix

    candidate = base_slug
    suffix = 1

    while User.objects.filter(username=candidate).exists():
        candidate = f"{base_slug}-{suffix}"
        suffix += 1

    return candidate


def _ensure_group_membership(user, group_name: Optional[str]):
    if not group_name:
        return

    group, _ = Group.objects.get_or_create(name=group_name)
    if not user.groups.filter(pk=group.pk).exists():
        user.groups.add(group)


def _ensure_profile_user(
    profile,
    email: str,
    name_attr: str,
    fallback_prefix: str,
    cpf_attr=None,
    group_name: Optional[str] = None,
):
    profile_user = getattr(profile, 'user', None)

    cpf_value = ''
    if cpf_attr:
        cpf_value = getattr(profile, cpf_attr, '') or ''
        cpf_value = cpf_value.strip()

    if profile_user:
        update_fields = []

        if email and not profile_user.email:
            profile_user.email = email
            update_fields.append('email')

        if cpf_value and profile_user.username != cpf_value:
            existing_cpf_user = (
                User.objects.filter(username=cpf_value)
                .exclude(pk=profile_user.pk)
                .first()
            )

            if existing_cpf_user:
                if email and not existing_cpf_user.email:
                    existing_cpf_user.email = email
                    existing_cpf_user.save(update_fields=['email'])

                setattr(profile, 'user', existing_cpf_user)
                profile.save(update_fields=['user'])
                _ensure_group_membership(existing_cpf_user, group_name)
                return existing_cpf_user

            profile_user.username = cpf_value
            update_fields.append('username')

            if email and profile_user.email != email:
                profile_user.email = email
                if 'email' not in update_fields:
                    update_fields.append('email')

        if update_fields:
            profile_user.save(update_fields=update_fields)

        _ensure_group_membership(profile_user, group_name)
        return profile_user

    user = None

    if cpf_value:
        user = User.objects.filter(username=cpf_value).first()
        if user:
            if email and not user.email:
                user.email = email
                user.save(update_fields=['email'])
            _ensure_group_membership(user, group_name)
        else:
            user = User.objects.create_user(username=cpf_value, email=email or '')
            _ensure_group_membership(user, group_name)

    if not user:
        display_name = getattr(profile, name_attr, '')
        email_slug = email.split('@')[0] if email and '@' in email else email
        username = _build_unique_username(display_name or email_slug, fallback_prefix)
        user = User.objects.create_user(username=username, email=email or '')
        _ensure_group_membership(user, group_name)

    setattr(profile, 'user', user)
    profile.save(update_fields=['user'])

    _ensure_group_membership(user, group_name)
    return user


def _resolve_user_from_email(email: str):
    if not email:
        return None

    responsavel = (
        Responsavel.objects.filter(email=email)
        .select_related('user')
        .first()
    )
    if responsavel:
        return _ensure_profile_user(
            responsavel,
            email,
            'name',
            'responsavel',
            'cpf',
            group_name='Responsavel',
        )

    aluno = (
        Aluno.objects.filter(email_aluno=email)
        .select_related('user')
        .first()
    )
    if aluno:
        return _ensure_profile_user(
            aluno,
            email,
            'name_aluno',
            'aluno',
            'cpf_aluno',
            group_name='Aluno',
        )

    professor = (
        Professor.objects.filter(email_professor=email)
        .select_related('user')
        .first()
    )
    if professor:
        return _ensure_profile_user(
            professor,
            email,
            'name_professor',
            'professor',
            'cpf_professor',
            group_name='Professor',
        )

    return User.objects.filter(email=email).first()


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        user = _resolve_user_from_email(email)

        if not user:
            return Response({'success': 'Se um usuário com este e-mail existir, um link de redefinição foi enviado.'}, status=status.HTTP_200_OK)

        PasswordResetToken.objects.filter(user=user).delete()

        token_obj = PasswordResetToken.objects.create(user=user)

        reset_link = f"http://localhost:5173/resetar-senha/{token_obj.token}"

        subject = 'Seu link de redefinição de senha'
        message = f'Olá, {user.first_name}.\n\nClique no link a seguir para redefinir sua senha:\n{reset_link}\n\nEste link expira em 1 hora.'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

        return Response({'success': 'Se um usuário com este e-mail existir, um link de redefinição foi enviado.'}, status=status.HTTP_200_OK)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token_from_request = (request.data.get('token') or '').strip()
        new_password = request.data.get('password')

        if not token_from_request or not new_password:
            return Response({'error': 'Token inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token_obj = (
                PasswordResetToken.objects.select_related('user')
                .get(token=token_from_request)
            )
        except (PasswordResetToken.DoesNotExist, ValueError):
            return Response({'error': 'Token inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        if token_obj.created_at < timezone.now() - timedelta(hours=1):
            token_obj.delete()
            return Response({'error': 'O token de redefinição expirou.'}, status=status.HTTP_400_BAD_REQUEST)

        user = token_obj.user
        user.set_password(new_password)
        user.save()

        token_obj.delete()

        return Response({'success': 'Senha redefinida com sucesso!'}, status=status.HTTP_200_OK)