from rest_framework import viewsets
from rest_framework.permissions import AllowAny
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
    permission_classes = [AllowAny]

class ProfessorViewSet(viewsets.ModelViewSet):
    queryset = Professor.objects.all()
    serializer_class = ProfessorSerializer
    permission_classes = [AllowAny]

class AlunoViewSet(viewsets.ModelViewSet):
    queryset = Aluno.objects.all()
    serializer_class = AlunoSerializer
    permission_classes = [AllowAny]

# ViewSets com Permissões Múltiplas e Filtros de Objeto
class NotaViewSet(viewsets.ModelViewSet):
    queryset = Nota.objects.all()
    serializer_class = NotaSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Nota.objects.all()

    def get_permissions(self):
        return [AllowAny()]

class AtividadePendenteViewSet(viewsets.ModelViewSet):
    queryset = AtividadePendente.objects.all()
    serializer_class = AtividadePendenteSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return AtividadePendente.objects.all()

    def get_permissions(self):
        return [AllowAny()]

class PagamentoPendenteViewSet(viewsets.ModelViewSet):
    queryset = PagamentoPendente.objects.all()
    serializer_class = PagamentoPendenteSerializer
    permission_classes = [AllowAny]

class AdvertenciaViewSet(viewsets.ModelViewSet):
    queryset = Advertencia.objects.all()
    serializer_class = AdvertenciaSerializer
    permission_classes = [AllowAny]

class SuspensaoViewSet(viewsets.ModelViewSet):
    queryset = Suspensao.objects.all()
    serializer_class = SuspensaoSerializer
    permission_classes = [AllowAny]

class EventoExtracurricularViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EventoExtracurricular.objects.all()
    serializer_class = EventoExtracurricularSerializer
    permission_classes = [AllowAny]

class EventoCalendarioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EventoCalendario.objects.all()
    serializer_class = EventoCalendarioSerializer
    permission_classes = [AllowAny]

class LivroViewSet(viewsets.ModelViewSet):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer
    permission_classes = [AllowAny]

class EmprestimoLivroViewSet(viewsets.ModelViewSet):
    queryset = EmprestimoLivro.objects.all()
    serializer_class = EmprestimoLivroSerializer
    permission_classes = [AllowAny]

class BimestreViewSet(viewsets.ModelViewSet):
    queryset = Bimestre.objects.all()
    serializer_class = BimestreSerializer
    permission_classes = [AllowAny]