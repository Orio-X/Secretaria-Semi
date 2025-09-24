from rest_framework import serializers
from .models import (
    Responsavel, Aluno, Professor, Bimestre, Nota, 
    AtividadePendente, EventoExtracurricular, PagamentoPendente, 
    Advertencia, Suspensao, EventoCalendario, EmprestimoLivro, Livro
)

# === Serializers Simples (Modelos sem chaves estrangeiras complexas) ===
# Esses serializers apenas expõem todos os campos do modelo.

class ResponsavelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Responsavel
        fields = '_all_'

class ProfessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professor
        fields = '_all_'

class BimestreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bimestre
        fields = '_all_'

class EventoExtracurricularSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventoExtracurricular
        fields = '_all_'

class EventoCalendarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventoCalendario
        fields = '_all_'

# === Serializers com Chaves Estrangeiras (Campos relacionados) ===
# Listamos explicitamente os campos para evitar ambiguidade entre os campos
# originais (ex: 'aluno') e os campos personalizados para escrita (ex: 'aluno_id').

class AlunoSerializer(serializers.ModelSerializer):
    # Campo para leitura, que retorna a representação em string do Responsavel
    responsavel_nome = serializers.StringRelatedField(source='Responsavel', read_only=True)
    
    # Campo para escrita, que recebe o ID do Responsavel
    responsavel = serializers.PrimaryKeyRelatedField(
        queryset=Responsavel.objects.all(),
        source='Responsavel',
        write_only=True
    )

    class Meta:
        model = Aluno
        # Listando todos os campos explicitamente.
        # Note que o campo 'Responsavel' é o campo original do modelo.
        # E o 'responsavel_nome' é o campo de leitura.
        fields = [
            'id', 'name_aluno', 'phone_number_aluno', 'email_aluno', 'cpf_aluno', 
            'birthday_aluno', 'class_choice', 'month_choice', 'faltas_aluno', 
            'ano_letivo', 'responsavel', 'responsavel_nome'
        ]

class NotaSerializer(serializers.ModelSerializer):
    # Campos de leitura.
    aluno_nome = serializers.StringRelatedField(source='aluno', read_only=True)
    bimestre_numero = serializers.StringRelatedField(source='bimestre', read_only=True)

    # Campos de escrita.
    aluno = serializers.PrimaryKeyRelatedField(queryset=Aluno.objects.all(), write_only=True)
    bimestre = serializers.PrimaryKeyRelatedField(queryset=Bimestre.objects.all(), write_only=True)

    class Meta:
        model = Nota
        fields = [
            'id', 'aluno', 'aluno_nome', 'bimestre', 'bimestre_numero', 'valor', 'disciplina'
        ]

class AtividadePendenteSerializer(serializers.ModelSerializer):
    aluno_nome = serializers.StringRelatedField(source='aluno', read_only=True)
    bimestre_numero = serializers.StringRelatedField(source='bimestre', read_only=True)
    
    aluno = serializers.PrimaryKeyRelatedField(queryset=Aluno.objects.all(), write_only=True)
    bimestre = serializers.PrimaryKeyRelatedField(queryset=Bimestre.objects.all(), write_only=True)

    class Meta:
        model = AtividadePendente
        fields = [
            'id', 'aluno', 'aluno_nome', 'bimestre', 'bimestre_numero', 'disciplina', 'descricao'
        ]

class PagamentoPendenteSerializer(serializers.ModelSerializer):
    aluno_nome = serializers.StringRelatedField(source='aluno', read_only=True)
    aluno = serializers.PrimaryKeyRelatedField(queryset=Aluno.objects.all(), write_only=True)

    class Meta:
        model = PagamentoPendente
        fields = ['id', 'aluno', 'aluno_nome', 'valor', 'data_vencimento', 'descricao']

class AdvertenciaSerializer(serializers.ModelSerializer):
    aluno_nome = serializers.StringRelatedField(source='aluno', read_only=True)
    aluno = serializers.PrimaryKeyRelatedField(queryset=Aluno.objects.all(), write_only=True)

    class Meta:
        model = Advertencia
        fields = ['id', 'aluno', 'aluno_nome', 'data', 'motivo', 'observacao']

class SuspensaoSerializer(serializers.ModelSerializer):
    aluno_nome = serializers.StringRelatedField(source='aluno', read_only=True)
    aluno = serializers.PrimaryKeyRelatedField(queryset=Aluno.objects.all(), write_only=True)

    class Meta:
        model = Suspensao
        fields = ['id', 'aluno', 'aluno_nome', 'data_inicio', 'data_fim', 'motivo', 'observacao']

class LivroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Livro
        fields = '_all_'

class EmprestimoLivroSerializer(serializers.ModelSerializer):
    # Campos de leitura (GET)
    aluno_nome = serializers.StringRelatedField(source='aluno', read_only=True)
    livro_titulo = serializers.StringRelatedField(source='livro', read_only=True)

    # Campos de escrita (POST/PUT)
    aluno = serializers.PrimaryKeyRelatedField(
        queryset=Aluno.objects.all(), 
        write_only=True
    )
    livro = serializers.PrimaryKeyRelatedField(
        queryset=Livro.objects.all(), 
        write_only=True,
        required=False,  # O livro não é obrigatório se for um computador
        allow_null=True
    )
    
    class Meta:
        model = EmprestimoLivro
        fields = [
            'id', 'aluno', 'aluno_nome', 'livro', 'livro_titulo', 'tipo', 
            'computador', 'data_emprestimo', 'data_devolucao', 'devolvido'
        ]