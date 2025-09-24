from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Responsavel, Aluno, Professor, Bimestre, Nota, AtividadePendente, EventoExtracurricular, PagamentoPendente, Advertencia, Suspensao, EventoCalendario, EmprestimoLivro, Livro
from .serializers import ResponsavelSerializer, AlunoSerializer, ProfessorSerializer, BimestreSerializer, NotaSerializer, AtividadePendenteSerializer, EventoExtracurricularSerializer, PagamentoPendenteSerializer, AdvertenciaSerializer, SuspensaoSerializer, EventoCalendarioSerializer, EmprestimoLivroSerializer, LivroSerializer
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