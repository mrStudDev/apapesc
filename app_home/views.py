from django.shortcuts import render
from django.contrib.auth.models import Group

def HomeView(request):
    context = {}

    if request.user.is_authenticated:
        context['is_superuser'] = request.user.is_superuser
        context['is_admin_associacao'] = request.user.groups.filter(name='Admin da Associação').exists()
        context['is_delegado_reparticao'] = request.user.groups.filter(name='Delegado(a) da Repartição').exists()

    return render(request, 'app_home/home.html', context)
