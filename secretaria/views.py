from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import (
    Responsavel, Aluno, Professor, Bimestre, Nota, AtividadePendente, 
    EventoExtracurricular, PagamentoPendente, Advertencia, Suspensao, 
    EventoCalendario, EmprestimoLivro, Livro, Tarefa
)
from .serializers import (
    ResponsavelSerializer, AlunoSerializer, ProfessorSerializer, BimestreSerializer, 
    NotaSerializer, AtividadePendenteSerializer, EventoExtracurricularSerializer, 
    PagamentoPendenteSerializer, AdvertenciaSerializer, SuspensaoSerializer, 
    EventoCalendarioSerializer, EmprestimoLivroSerializer, LivroSerializer, 
    TarefaSerializer
)
from .permissions import IsSecretaria, IsProfessor, IsResponsavel, IsAluno
from rest_framework.decorators import action

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
    permission_classes = [IsSecretaria]

class ProfessorViewSet(viewsets.ModelViewSet):
    queryset = Professor.objects.all()
    serializer_class = ProfessorSerializer
    permission_classes = [IsSecretaria]

class AlunoViewSet(viewsets.ModelViewSet):
    queryset = Aluno.objects.all()
    serializer_class = AlunoSerializer
    permission_classes = [IsSecretaria]

# ViewSets com Permissões Múltiplas e Filtros de Objeto
class NotaViewSet(viewsets.ModelViewSet):
    queryset = Nota.objects.all()
    serializer_class = NotaSerializer

    def get_queryset(self):
        user = self.request.user
        if IsSecretaria().has_permission(self.request, self) or IsProfessor().has_permission(self.request, self):
            return Nota.objects.all()
        elif IsResponsavel().has_permission(self.request, self):
            return Nota.objects.filter(aluno__Responsavel__user=user)
        elif IsAluno().has_permission(self.request, self):
            return Nota.objects.filter(aluno__user=user)
        
        return Nota.objects.none()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsSecretaria | IsProfessor]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

class AtividadePendenteViewSet(viewsets.ModelViewSet):
    queryset = AtividadePendente.objects.all()
    serializer_class = AtividadePendenteSerializer

    def get_queryset(self):
        user = self.request.user
        if IsSecretaria().has_permission(self.request, self) or IsProfessor().has_permission(self.request, self):
            return AtividadePendente.objects.all()
        elif IsResponsavel().has_permission(self.request, self):
            return AtividadePendente.objects.filter(aluno__Responsavel__user=user)
        elif IsAluno().has_permission(self.request, self):
            return AtividadePendente.objects.filter(aluno__user=user)
        
        return AtividadePendente.objects.none()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsSecretaria | IsProfessor]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

# ... (Restante das suas Views originais) ...

class PagamentoPendenteViewSet(viewsets.ModelViewSet):
    queryset = PagamentoPendente.objects.all()
    serializer_class = PagamentoPendenteSerializer
    # ... (lógica de permissões) ...

class AdvertenciaViewSet(viewsets.ModelViewSet):
    queryset = Advertencia.objects.all()
    serializer_class = AdvertenciaSerializer
    # ... (lógica de permissões) ...

class SuspensaoViewSet(viewsets.ModelViewSet):
    queryset = Suspensao.objects.all()
    serializer_class = SuspensaoSerializer
    # ... (lógica de permissões) ...

class EventoExtracurricularViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EventoExtracurricular.objects.all()
    serializer_class = EventoExtracurricularSerializer
    permission_classes = [IsAuthenticated]

class EventoCalendarioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EventoCalendario.objects.all()
    serializer_class = EventoCalendarioSerializer
    permission_classes = [IsAuthenticated]

class LivroViewSet(viewsets.ModelViewSet):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer
    # ... (lógica de permissões) ...

class EmprestimoLivroViewSet(viewsets.ModelViewSet):
    queryset = EmprestimoLivro.objects.all()
    serializer_class = EmprestimoLivroSerializer
    # ... (lógica de permissões) ...

class BimestreViewSet(viewsets.ModelViewSet):
    queryset = Bimestre.objects.all()
    serializer_class = BimestreSerializer
    # ... (lógica de permissões) ...

# <--- NOVO VIEWSET DE TAREFA ADICIONADO ABAIXO --->
class TarefaViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite que tarefas sejam visualizadas ou editadas.
    Filtra as tarefas com base no perfil do usuário.
    """
    serializer_class = TarefaSerializer

    def get_queryset(self):
        user = self.request.user
        
        # Secretaria e Professores podem ver todas as tarefas
        if IsSecretaria().has_permission(self.request, self) or IsProfessor().has_permission(self.request, self):
            queryset = Tarefa.objects.all()
        # Responsáveis veem as tarefas dos seus alunos
        elif IsResponsavel().has_permission(self.request, self):
            queryset = Tarefa.objects.filter(aluno__Responsavel__user=user)
        # Alunos veem apenas suas próprias tarefas
        elif IsAluno().has_permission(self.request, self):
            queryset = Tarefa.objects.filter(aluno__user=user)
        else:
            return Tarefa.objects.none()

        # Permite que professores/secretaria filtrem por um aluno específico via URL
        # Exemplo: /api/tarefas/?aluno_id=5
        aluno_id = self.request.query_params.get('aluno_id', None)
        if aluno_id is not None and (IsSecretaria().has_permission(self.request, self) or IsProfessor().has_permission(self.request, self)):
            queryset = queryset.filter(aluno__id=aluno_id)
            
        return queryset

    def get_permissions(self):
        # Apenas Secretaria e Professores podem criar, editar ou deletar tarefas
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsSecretaria | IsProfessor]
        # Todos os usuários autenticados podem listar/ver tarefas (já filtradas pelo get_queryset)
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()