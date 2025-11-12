# secretaria/serializers.py
import re

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Q
# --- CORREÇÃO IMPORTANTE APLICADA AQUI ---
from django.contrib.auth import authenticate # Importamos a função que faltava

# --- [ADICIONADO] Imports para a nova regra de permissão ---
from django.utils import timezone
from .permissions import IsProfessor
# Usamos 'import .views' para evitar importação circular
from . import views 

from django.contrib.auth.models import User
import random
import string
from django.db import transaction
from django.contrib.auth.models import Group
# -----------------------------------------------------------

from .models import (
    Responsavel, Aluno, Professor, Bimestre, Nota, 
    AtividadePendente, EventoExtracurricular, # <-- [CORRIGIDO] Removida duplicata
    PlanejamentoSemanal, 
    Advertencia, Suspensao, EventoCalendario, EmprestimoLivro, Livro, 
    Sala, Reserva
)

# === CLASSE DE AUTENTICAÇÃO ATUALIZADA (VERSÃO MAIS ROBUSTA) ===
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'cpf'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Adiciona o username (CPF)
        token['username'] = user.username
        
        # Buscamos o primeiro "Grupo" (cargo) do usuário e o adicionamos ao token.
        cargo = None
        if user.groups.exists():
            cargo = user.groups.first().name  # Pega o nome (ex: "Secretaria", "Professor")
        
        token['cargo'] = cargo # Adiciona a chave 'cargo' ao token

        return token

    def _normalize_identifier(self, identifier: str):
        """Return only CPF digits when a valid identifier is provided."""
        identifier = (identifier or '').strip()
        if not identifier:
            return ''

        digits_only = re.sub(r'\D', '', identifier)
        if len(digits_only) == 11:
            return digits_only

        return ''

    def validate(self, attrs):
        identifier = attrs.get('cpf')
        password = attrs.get('password')

        if not identifier or not password:
            raise serializers.ValidationError('CPF e senha são obrigatórios.', code='authorization')

        normalized_username = self._normalize_identifier(identifier)

        if not normalized_username:
            raise serializers.ValidationError('CPF ou senha inválidos.', code='authorization')

        user = authenticate(
            request=self.context.get('request'),
            username=normalized_username,
            password=password,
        )

        if not user and normalized_username != identifier:
            user = authenticate(
                request=self.context.get('request'),
                username=identifier,
                password=password,
            )

        if not user:
            raise serializers.ValidationError('CPF ou senha inválidos.', code='authorization')

        self.user = user
        refresh = self.get_token(user)

        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return data


class ResponsavelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Responsavel
        fields = '__all__'
        read_only_fields = ('user',) 

    @transaction.atomic
    def create(self, validated_data):
        # 1. Dados para o User
        email = validated_data['email']
        cpf = validated_data['cpf']
        name = validated_data['name']
        
        # 2. Gera senha aleatória
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        
        # 3. Cria o objeto User do Django
        try:
            user = User.objects.create_user(
                username=cpf, 
                email=email,
                password=password, 
                first_name=name.split(' ')[0],
                last_name=' '.join(name.split(' ')[1:]),
                is_staff=True, # Mantenha como True se eles acessarem o Admin para qualquer coisa
            )
            responsavel_group = Group.objects.get(name='Responsavel')
            user.groups.add(responsavel_group)
        except Exception as e:
            raise serializers.ValidationError({'detail': f'Não foi possível criar o usuário de login. Erro: {e}'})

        # 4. Cria o objeto Responsavel e associa o User
        validated_data['user'] = user
        return Responsavel.objects.create(**validated_data)

class ProfessorSerializer(serializers.ModelSerializer):
    disciplina_label = serializers.CharField(source='get_disciplina_display', read_only=True)
    
    class Meta:
        model = Professor
        fields = '__all__'
        read_only_fields = ('user',) # Garante que 'user' não pode ser modificado na edição

    @transaction.atomic # Garante que, se falhar, nada é salvo
    def create(self, validated_data):
        # 1. Dados para o User
        email = validated_data['email_professor']
        cpf = validated_data['cpf_professor']
        name = validated_data['name_professor']
        
        # 2. Gera uma senha aleatória (mantendo seu fluxo de segurança)
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

        # 3. Cria o objeto User do Django
        try:
            user = User.objects.create_user(
                username=cpf, # CPF como username para login
                email=email,
                password=password, # Senha hashada automaticamente
                first_name=name.split(' ')[0],
                last_name=' '.join(name.split(' ')[1:]),
                is_staff=True, # Professores devem ser is_staff para acessar o admin/permissões
            )
            professor_group = Group.objects.get(name='Professor')
            user.groups.add(professor_group)
        except Exception as e:
            # Se a criação falhar (ex: CPF já usado), lança exceção do Serializer
            raise serializers.ValidationError({'detail': f'Não foi possível criar o usuário de login. Erro: {e}'})

        # 4. Cria o objeto Professor e associa o User
        validated_data['user'] = user
        professor = Professor.objects.create(**validated_data)
        
        # Opcional: Logar a senha temporária para fins de depuração
        print(f"Usuário Professor criado com a senha temporária: {password}")

        return professor

# -----------------------------------------------------------------
# --- AJUSTES APLICADOS NESTA CLASSE (AlunoSerializer) ---
# -----------------------------------------------------------------
class AlunoSerializer(serializers.ModelSerializer):
    responsavel_nome = serializers.StringRelatedField(source='Responsavel', read_only=True)
    
    Responsavel = serializers.PrimaryKeyRelatedField(queryset=Responsavel.objects.all())
    
    faltas_aluno = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Aluno
        fields = [
            'id', 'user', 'name_aluno', 'phone_number_aluno', 'email_aluno', 'cpf_aluno', 
            'birthday_aluno', 'class_choice', 'month_choice', 'faltas_aluno', 
            'ano_letivo', 
            'Responsavel',
            'responsavel_nome', 
            'comentario_descritivo',
            'presencas_aluno',
            'ativo' ,
            'aluno_nota', 
        ]
        read_only_fields = ('user',) # Garante que 'user' não pode ser modificado na edição

    @transaction.atomic
    def create(self, validated_data):
        # 1. Dados para o User
        email = validated_data['email_aluno']
        cpf = validated_data['cpf_aluno']
        name = validated_data['name_aluno']
        
        # 2. Gera senha aleatória
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

        # 3. Cria o objeto User do Django
        try:
            user = User.objects.create_user(
                username=cpf, 
                email=email,
                password=password, 
                first_name=name.split(' ')[0],
                last_name=' '.join(name.split(' ')[1:]),
                is_staff=False, # Alunos NÃO devem ser is_staff
            )
            aluno_group = Group.objects.get(name='Aluno')
            user.groups.add(aluno_group)
        except Exception as e:
            raise serializers.ValidationError({'detail': f'Não foi possível criar o usuário de login. Erro: {e}'})

        # 4. Cria o objeto Aluno e associa o User
        validated_data['user'] = user
        return Aluno.objects.create(**validated_data)


class BimestreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bimestre
        fields = '__all__'

class NotaSerializer(serializers.ModelSerializer):
    aluno_nome = serializers.StringRelatedField(source='aluno', read_only=True)
    bimestre_numero = serializers.StringRelatedField(source='bimestre', read_only=True)
    
    aluno = serializers.PrimaryKeyRelatedField(queryset=Aluno.objects.all(), write_only=True)
    
    bimestre = serializers.PrimaryKeyRelatedField(queryset=Bimestre.objects.all()) 
    
    class Meta:
        model = Nota
        fields = [
            'id', 'aluno', 'aluno_nome', 'bimestre', 'bimestre_numero', 'valor', 'disciplina'
        ]

class AtividadePendenteSerializer(serializers.ModelSerializer):
    aluno_nome = serializers.StringRelatedField(source='aluno', read_only=True)
    
    aluno = serializers.PrimaryKeyRelatedField(queryset=Aluno.objects.all(), write_only=True)
    
    class Meta:
        model = AtividadePendente
        fields = [
            'id', 'aluno', 'aluno_nome', 
            'titulo', 'descricao', 'data_limite', 'status', 'data_criacao'
        ]
        extra_kwargs = {
            'data_criacao': {'read_only': True},
        }

class PlanejamentoSemanalSerializer(serializers.ModelSerializer):
    professor_nome = serializers.CharField(source='professor.name_professor', read_only=True)
    
    class Meta:
        model = PlanejamentoSemanal
        fields = '__all__'

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

class EventoExtracurricularSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventoExtracurricular
        fields = '__all__'

class EventoCalendarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventoCalendario
        fields = '__all__'

class LivroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Livro
        fields = '__all__'

class EmprestimoLivroSerializer(serializers.ModelSerializer):
    aluno_nome = serializers.StringRelatedField(source='aluno', read_only=True)
    livro_titulo = serializers.StringRelatedField(source='livro', read_only=True)
    
    aluno = serializers.PrimaryKeyRelatedField(
        queryset=Aluno.objects.all(), 
        write_only=True
    )
    livro = serializers.PrimaryKeyRelatedField(
        queryset=Livro.objects.all(), 
        write_only=True,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = EmprestimoLivro
        fields = [
            'id', 'aluno', 'aluno_nome', 'livro', 'livro_titulo', 
            'tipo', 'computador', 'data_emprestimo', 'data_devolucao', 'devolvido'
        ]
    
class SalaSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = Sala
        fields = ['id', 'nome', 'tipo', 'tipo_display', 'capacidade', 'recursos']

# =================================================================
# --- [ALTERAÇÕES] ReservaSerializer ---
# =================================================================
class ReservaSerializer(serializers.ModelSerializer):
    sala_nome = serializers.StringRelatedField(source='sala', read_only=True)
    professor_nome = serializers.StringRelatedField(source='professor', read_only=True)
    
    class Meta:
        model = Reserva
        fields = '__all__'
        # unique_together = (('sala', 'data', 'horario_inicio'),) # Comentado, pois 'validate' faz checagem mais robusta

    def validate(self, data):
        """
        1. Verifica conflito de horário (lógica existente).
        2. [NOVO] Verifica limite de 1 reserva ativa para Professor.
        """
        
        # --- Lógica de conflito de horário (lógica existente) ---
        # Obter os dados da nova reserva
        # Se 'data.get' falhar, usa o 'instance' (para PATCH)
        sala = data.get('sala', getattr(self.instance, 'sala', None))
        data_reserva = data.get('data', getattr(self.instance, 'data', None))
        inicio = data.get('horario_inicio', getattr(self.instance, 'horario_inicio', None))
        fim = data.get('horario_fim', getattr(self.instance, 'horario_fim', None))
        
        instance = self.instance

        if inicio >= fim:
            raise serializers.ValidationError({"horario_fim": "O horário de término deve ser posterior ao horário de início."})
        
        reservas_conflitantes = Reserva.objects.filter(
            sala=sala,
            data=data_reserva
        ).filter(
            Q(horario_inicio__lt=fim) & Q(horario_fim__gt=inicio)
        )
        
        # Excluir a instância atual se for uma atualização
        if instance:
            reservas_conflitantes = reservas_conflitantes.exclude(pk=instance.pk)
        
        if reservas_conflitantes.exists():
            conflito = reservas_conflitantes.first()
            raise serializers.ValidationError(
                f"Conflito de horário: A sala {sala.nome} já está reservada das {conflito.horario_inicio.strftime('%H:%M')} às {conflito.horario_fim.strftime('%H:%M')}."
            )
        
        # --- [REGRA] Professor: Limite de 1 reserva ativa ---
        # Pega o usuário do contexto da requisição (fornecido pelo ViewSet)
        user = self.context['request'].user
        
        # Se o usuário for um professor (e não Secretaria criando)
        if IsProfessor().has_permission(self.context['request'], self):
            # Usamos a view importada para evitar importação circular
            professor = views.get_professor_by_user(user) 
            if professor:
                agora = timezone.now().date()
                
                # Contar reservas ativas (data de hoje ou no futuro)
                reservas_ativas = Reserva.objects.filter(
                    professor=professor,
                    data__gte=agora
                )
                
                # Se for 'update' (edição), exclui a si mesmo da contagem
                if instance:
                    reservas_ativas = reservas_ativas.exclude(pk=instance.pk)

                # Se já tiver 1 ou mais reservas, bloqueia
                if reservas_ativas.count() >= 1:
                    raise serializers.ValidationError(
                        "Limite atingido: Professores só podem ter 1 reserva ativa (futura) por vez."
                    )

        # Se passou em todas as validações
        return data