from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.urls import reverse
from django.contrib.auth.signals import user_logged_in
from django.shortcuts import redirect
from django.http import HttpResponseRedirect


@receiver(pre_save, sender=User)
def validate_user_fields(sender, instance, **kwargs):
    if not instance.first_name or not instance.last_name:
        raise ValidationError("Nome e sobrenome são obrigatórios.")


@receiver(user_logged_in)
def redirect_user_based_on_group(sender, request, user, **kwargs):
    # Redireciona baseado no grupo do usuário
    if user.is_superuser:
        return HttpResponseRedirect(reverse('super_dashboard'))
    elif user.groups.filter(name='Admin da Associação').exists():
        return HttpResponseRedirect(reverse('admin_dashboard'))
    elif user.groups.filter(name='Delegado(a) da Repartição').exists():
        return HttpResponseRedirect(reverse('delegado_dashboard'))
    elif user.groups.filter(name='Auxiliar da Associação').exists():
        return HttpResponseRedirect(reverse('auxiliar_associacao_dashboard'))
    elif user.groups.filter(name='Auxiliar da Repartição').exists():
        return HttpResponseRedirect(reverse('auxiliar_reparticao_dashboard'))
    elif user.groups.filter(name='Diretor(a) da Associação').exists():
        return HttpResponseRedirect(reverse('diretor_associacao_dashboard'))
    elif user.groups.filter(name='Presidente da Associação').exists():
        return HttpResponseRedirect(reverse('presidente_associacao_dashboard'))
    elif user.groups.filter(name='Associados da Associação').exists():
        return HttpResponseRedirect(reverse('associado_dashboard'))
    else:
        # Redireciona para home caso nenhum grupo seja encontrado
        return HttpResponseRedirect(reverse('home'))