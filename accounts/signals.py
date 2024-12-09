from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save
from django.dispatch import receiver


@receiver(pre_save, sender=User)
def validate_user_fields(sender, instance, **kwargs):
    if not instance.first_name or not instance.last_name:
        raise ValidationError("Nome e sobrenome são obrigatórios.")
