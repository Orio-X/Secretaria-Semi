from rest_framework import permissions

class IsSecretaria(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                request.user.groups.filter(name='Secretaria').exists())

class IsProfessor(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                request.user.groups.filter(name='Professor').exists())

class IsResponsavel(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                request.user.groups.filter(name='Responsavel').exists())

class IsAluno(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                request.user.groups.filter(name='Aluno').exists())

class IsAuxiliarAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                request.user.groups.filter(name='Auxiliar administrativo').exists())

# Permissões combinadas usando | (OR)
class IsSecretariaOrAuxiliarAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (IsSecretaria().has_permission(request, view) or 
                IsAuxiliarAdmin().has_permission(request, view))

class IsSecretariaOrProfessor(permissions.BasePermission):
    def has_permission(self, request, view):
        return (IsSecretaria().has_permission(request, view) or 
                IsProfessor().has_permission(request, view))

class IsSecretariaOrAuxiliarOrProfessor(permissions.BasePermission):
    def has_permission(self, request, view):
        return (IsSecretaria().has_permission(request, view) or 
                IsAuxiliarAdmin().has_permission(request, view) or
                IsProfessor().has_permission(request, view))

# Novas permissões específicas
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas o proprietário de um objeto o edite.
    """
    def has_object_permission(self, request, view, obj):
        # Permissões de leitura são permitidas para qualquer requisição
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permissões de escrita são permitidas apenas para o proprietário
        return obj.user == request.user

class IsAlunoOwner(permissions.BasePermission):
    """
    Permissão para ver apenas dados do próprio aluno
    """
    def has_permission(self, request, view):
        # Permite acesso se for aluno
        return IsAluno().has_permission(request, view)
    
    def has_object_permission(self, request, view, obj):
        # Verifica se o usuário é um aluno e se o objeto pertence a ele
        if hasattr(obj, 'usuario'):
            return obj.usuario == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'aluno') and hasattr(obj.aluno, 'usuario'):
            return obj.aluno.usuario == request.user
        elif hasattr(obj, 'aluno') and hasattr(obj.aluno, 'user'):
            return obj.aluno.user == request.user
        return False

class IsResponsavelRelated(permissions.BasePermission):
    """
    Permissão para responsáveis verem apenas dados dos seus alunos
    """
    def has_permission(self, request, view):
        # Permite acesso se for responsável
        return IsResponsavel().has_permission(request, view)
    
    def has_object_permission(self, request, view, obj):
        from secretaria.models import Aluno  # Import aqui para evitar circular imports
        
        if not IsResponsavel().has_permission(request, view):
            return False
            
        try:
            # Para objetos Aluno diretamente
            if isinstance(obj, Aluno):
                return obj.responsavel == request.user
            
            # Para objetos que têm relação com Aluno
            elif hasattr(obj, 'aluno'):
                return obj.aluno.responsavel == request.user
                
            # Para objetos que têm relação com usuário
            elif hasattr(obj, 'usuario'):
                # Verificar se o usuário é um aluno vinculado a este responsável
                try:
                    aluno = Aluno.objects.get(usuario=obj.usuario)
                    return aluno.responsavel == request.user
                except Aluno.DoesNotExist:
                    return False
                    
        except Exception:
            return False
            
        return False

class IsProfessorOrSecretariaOrAuxiliar(permissions.BasePermission):
    """
    Permissão para Professores, Secretaria e Auxiliar Admin
    """
    def has_permission(self, request, view):
        return (IsProfessor().has_permission(request, view) or 
                IsSecretaria().has_permission(request, view) or
                IsAuxiliarAdmin().has_permission(request, view))

class CanCreateUpdateDeleteEmprestimo(permissions.BasePermission):
    """
    Permissão específica para criar/editar/deletar empréstimos
    """
    def has_permission(self, request, view):
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return (IsSecretaria().has_permission(request, view) or 
                    IsAuxiliarAdmin().has_permission(request, view))
        return True  # GET, HEAD, OPTIONS são permitidos para autenticados

class CanAccessReservas(permissions.BasePermission):
    """
    Permissão para acessar reservas (Professores podem criar, Secretaria/Auxiliar podem tudo)
    """
    def has_permission(self, request, view):
        if request.method == 'POST':
            # Professores, Secretaria e Auxiliar podem criar reservas
            return (IsProfessor().has_permission(request, view) or 
                    IsSecretaria().has_permission(request, view) or
                    IsAuxiliarAdmin().has_permission(request, view))
        else:
            # Secretaria e Auxiliar podem ver/editar todas as reservas
            if IsSecretaria().has_permission(request, view) or IsAuxiliarAdmin().has_permission(request, view):
                return True
            # Professores só podem ver suas próprias reservas
            elif IsProfessor().has_permission(request, view):
                return True
        return False

# Permissões para viewsets específicos
class EmprestimoPermission(permissions.BasePermission):
    """
    Permissão abrangente para empréstimos
    """
    def has_permission(self, request, view):
        # Todos os métodos precisam de autenticação
        if not request.user.is_authenticated:
            return False
            
        # Secretaria e Auxiliar têm acesso completo
        if IsSecretaria().has_permission(request, view) or IsAuxiliarAdmin().has_permission(request, view):
            return True
            
        # Responsáveis e Alunos só podem fazer GET
        if request.method in permissions.SAFE_METHODS:
            return (IsResponsavel().has_permission(request, view) or 
                    IsAluno().has_permission(request, view))
                    
        return False

class ReservaPermission(permissions.BasePermission):
    """
    Permissão abrangente para reservas
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # Secretaria e Auxiliar têm acesso completo
        if IsSecretaria().has_permission(request, view) or IsAuxiliarAdmin().has_permission(request, view):
            return True
            
        # Professores podem criar e ver suas reservas
        if IsProfessor().has_permission(request, view):
            if request.method == 'POST':
                return True
            elif request.method in permissions.SAFE_METHODS:
                return True
                
        return False

# Permissão para debug
class DebugPermission(permissions.BasePermission):
    """
    Permissão para debug - mostra informações detalhadas
    """
    def has_permission(self, request, view):
        print(f"=== DEBUG PERMISSION ===")
        print(f"Usuário: {request.user}")
        print(f"Grupos: {list(request.user.groups.all().values_list('name', flat=True))}")
        print(f"Método: {request.method}")
        print(f"View: {view.__class__.__name__}")
        print(f"Ação: {getattr(view, 'action', 'N/A')}")
        
        # Verifica todas as permissões básicas
        perms = {
            'Secretaria': IsSecretaria().has_permission(request, view),
            'AuxiliarAdmin': IsAuxiliarAdmin().has_permission(request, view),
            'Professor': IsProfessor().has_permission(request, view),
            'Responsavel': IsResponsavel().has_permission(request, view),
            'Aluno': IsAluno().has_permission(request, view),
        }
        print(f"Permissões: {perms}")
        print("=======================")
        
        # Permite acesso apenas para debug
        return request.user.is_staff  # Apenas staff pode usar para debug