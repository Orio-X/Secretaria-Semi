from django.contrib import admin
from django.utils.html import format_html
from secretaria.models import Responsavel, Aluno, Professor, Bimestre, Nota, AtividadePendente, EventoExtracurricular, PagamentoPendente, Advertencia, Suspensao, EventoCalendario, EmprestimoLivro, Livro 
from django.contrib.auth.models import Group, User
from django.apps import apps

# O admin.py define como os dados serão exibidos no painel de administração do Django (a parte visual). Também é onde você pode personalizar a exibição de varios elementos para melhorar a interface do usuário.

@admin.register(Responsavel)
class ResponsaveisAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_name', 'get_phone_number', 'get_email', 'get_adress', 'get_cpf', 'get_birthday')
    list_display_links = ('get_name',)
    search_fields = ('name', 'cpf',)
    list_filter = ('name', 'cpf',)

    # Substituí os nomes dos campos diretos por métodos customizados com 'short_description', em  'ResponsaveisAdmin', 'AlunosAdmin' e em 'ProfessorAdmin', pois o Django Admin exibia mensagens como "DIGITE O NOME DO RESPONSAVEL" no cabeçalho das colunas.

    def get_name(self, obj):
        return obj.name
    get_name.short_description = 'Nome do Responsável'

    def get_phone_number(self, obj):
        return obj.phone_number
    get_phone_number.short_description = 'Celular'

    def get_email(self, obj):
        return obj.email
    get_email.short_description = 'E-mail'

    def get_adress(self, obj):
        return obj.adress
    get_adress.short_description = 'Endereço'

    def get_cpf(self, obj):
        return obj.cpf
    get_cpf.short_description = 'CPF'

    def get_birthday(self, obj):
        return obj.birthday
    get_birthday.short_description = 'Data de Nascimento'

@admin.register(Aluno)
class AlunosAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_turma', 'get_nome', 'get_celular', 'get_email', 'get_cpf', 'birthday_aluno', 'faltas_aluno')
    list_display_links = ('get_nome',)
    search_fields = ('name_aluno', 'cpf_aluno',)
    list_filter = ('class_choice',)

    # Utilizacão de 'short_description' para correcação de cabeçalho das colunas

    def get_turma(self, obj):
        return obj.class_choice
    get_turma.short_description = 'Turma'

    def get_nome(self, obj):
        return obj.name_aluno
    get_nome.short_description = 'Nome do Aluno'

    def get_celular(self, obj):
        return obj.phone_number_aluno
    get_celular.short_description = 'Número de Celular'

    def get_email(self, obj):
        return obj.email_aluno
    get_email.short_description = 'E-mail do Aluno'

    def get_cpf(self, obj):
        return obj.cpf_aluno
    get_cpf.short_description = 'CPF do Aluno'

@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_name', 'get_phone', 'get_email','get_cpf', 'get_birthday', 'get_matricula')
    list_display_links = ('get_name',)
    search_fields = ('name_professor', 'cpf_professor',)
    list_filter = ('name_professor', 'cpf_professor',)

    # Utilizacão de 'short_description' para correcação de cabeçalho das colunas

    def get_name(self, obj):
        return obj.name_professor
    get_name.short_description = 'Nome do Professor'

    def get_phone(self, obj):
        return obj.phone_number_professor
    get_phone.short_description = 'Celular'

    def get_email(self, obj):
        return obj.email_professor
    get_email.short_description = 'E-mail'

    def get_cpf(self, obj):
        return obj.cpf_professor
    get_cpf.short_description = 'CPF'

    def get_birthday(self, obj):
        return obj.birthday_professor
    get_birthday.short_description = 'Nascimento'

    def get_matricula(self, obj):
        return obj.matricula_professor
    get_matricula.short_description = 'Matrícula'

@admin.register(Bimestre)
class BimestreAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero')
    list_filter = ('numero',)

@admin.register(EmprestimoLivro)
class EmprestimoMaterialAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo', 'livro', 'computador', 'aluno', 'data_emprestimo', 'devolvido', 'data_devolucao')
    list_filter = ('tipo', 'devolvido', 'data_emprestimo', 'livro', 'aluno')
    search_fields = ('livro__titulo', 'computador', 'aluno__complete_name_aluno')

@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'autor', 'data_publicacao')
    search_fields = ('titulo', 'autor')
    list_filter = ('data_publicacao', 'autor')

@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    list_display = ('id', 'aluno', 'disciplina', 'bimestre', 'valor')
    list_filter = ('bimestre', 'aluno__class_choice', 'aluno', 'disciplina')
    ordering = ('bimestre', 'aluno__class_choice', 'aluno', 'disciplina')

    def media_disciplina(self, obj):
        media = obj.aluno.media_por_disciplina(obj.disciplina) # calcula a média do aluno de determinada disciplina
        return f"{media:.1f}" if media is not None else "-"

    def alerta_baixo_desempenho(self, obj): 
        media = obj.aluno.media_por_disciplina(obj.disciplina) # exibe alerta se a média do aluno for abaixo de 6
        if media is not None and media < 6:
            return format_html(">Abaixo da média!")
        return ""

    media_disciplina.short_description = "Média Disciplina" 
    alerta_baixo_desempenho.short_description = "Alerta" 


@admin.register(AtividadePendente)
class AtividadePendenteAdmin(admin.ModelAdmin):
    list_display = ('id', 'aluno', 'disciplina', 'bimestre', 'descricao')
    list_filter = ('bimestre', 'aluno__class_choice','disciplina')
    ordering = ('bimestre', 'aluno__class_choice', 'disciplina')


@admin.register(EventoExtracurricular)
class EventoExtracurricularAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'data', 'professor_id')
    search_fields = ('titulo', 'professor_id')
    list_filter = ('data',)


@admin.register(PagamentoPendente)
class PagamentoPendenteAdmin(admin.ModelAdmin):
    list_display = ('id', 'aluno', 'valor', 'data_vencimento', 'descricao')
    search_fields = ('aluno__cpf_aluno',)
    list_filter = ('data_vencimento',)
    autocomplete_fields = ['aluno'] 

@admin.register(Advertencia)
class AdvertenciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'aluno', 'data', 'motivo')
    search_fields = ('aluno__cpf_aluno', 'aluno__name_aluno', 'motivo')
    list_filter = ('data', 'motivo',)
    autocomplete_fields = ['aluno']

@admin.register(Suspensao)
class SuspensaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'aluno', 'data_inicio', 'data_fim', 'motivo')
    search_fields = ('aluno__cpf_aluno', 'aluno__name_aluno', 'motivo')
    list_filter = ('data_inicio', 'data_fim', 'motivo',)
    autocomplete_fields = ['aluno']

@admin.register(EventoCalendario)
class EventoCalendarioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'data')
    list_filter = ('tipo', 'data')
    search_fields = ('titulo', 'descricao')


# Personalizei os nomes exibidos no admin com verbose_name e verbose_name_plural para tornar a interface mais compreensível 

apps.get_app_config('auth').verbose_name = 'Controle de Usuários'
admin.site.site_header = "Minha Escola"
admin.site.site_title = "Painel Administrativo"
admin.site.index_title = "Administração do Sistema"
Group._meta.verbose_name = "Grupo"
Group._meta.verbose_name_plural = "Grupos"
User._meta.verbose_name = "Usuário"
User._meta.verbose_name_plural = "Usuários"
