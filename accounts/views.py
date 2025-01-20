from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse


@login_required
def custom_login_redirect(request):
    user = request.user

    if user.is_superuser:
        return redirect(reverse('app_manager:super_dashboard'))
    elif user.groups.filter(name='Admin da Associação').exists():
        return redirect(reverse('app_manager:admin_dashboard'))
    elif user.groups.filter(name='Delegado(a) da Repartição').exists():
        return redirect(reverse('app_manager:delegado_dashboard'))
    elif user.groups.filter(name='Auxiliar da Associação').exists():
        return redirect(reverse('app_manager:auxiliar_associacao_dashboard'))
    elif user.groups.filter(name='Auxiliar da Repartição').exists():
        return redirect(reverse('app_manager:auxiliar_reparticao_dashboard'))
    elif user.groups.filter(name='Diretor(a) da Associação').exists():
        return redirect(reverse('app_manager:diretor_associacao_dashboard'))
    elif user.groups.filter(name='Presidente da Associação').exists():
        return redirect(reverse('app_manager:presidente_associacao_dashboard'))
    elif user.groups.filter(name='Associados da Associação').exists():
        return redirect(reverse('app_manager:associado_dashboard'))
    elif user.groups.filter(name='User Vip').exists():
        return redirect(reverse('app_manager:user_vip_dasboard'))
    else:
        # Fallback para home
        return redirect(reverse('app_home:home'))
