from django.contrib.auth.models import Group

def group_context(request):
    if not request.user.is_authenticated:
        return {}
    
    return {
        'is_superuser': request.user.is_superuser,
        'is_admin_associacao': request.user.groups.filter(name='Admin da Associação').exists(),
        'is_delegado_reparticao': request.user.groups.filter(name='Delegado(a) da Repartição').exists(),
        'is_auxiliar_associacao': request.user.groups.filter(name='Auxiliar da Associação').exists(),
        'is_auxiliar_reparticao': request.user.groups.filter(name='Auxiliar da Repartição').exists(),
        'is_diretor_associacao': request.user.groups.filter(name='Diretor(a) da Associação').exists(),
        'is_presidente_associacao': request.user.groups.filter(name='Presidente da Associação').exists(),
        'is_associado_associacao': request.user.groups.filter(name='Associados da Associação').exists(),
        'is_user_vip': request.user.groups.filter(name='User Vip').exists(),
    }
