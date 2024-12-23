from django.contrib.auth.mixins import UserPassesTestMixin

class GroupPermissionRequiredMixin(UserPassesTestMixin):
    group_required = None  # Pode ser string ou lista de grupos

    def test_func(self):
        user = self.request.user

        # Verificar se o usuário está autenticado
        if not user.is_authenticated:
            return False

        # Verificar se o usuário é superusuário
        if user.is_superuser:
            return True

        # Verificar se o grupo é uma string ou lista e checar a permissão
        if self.group_required:
            if isinstance(self.group_required, str):
                self.group_required = [self.group_required]  # Converte para lista se for string
            return user.groups.filter(name__in=self.group_required).exists()

        return False

    def handle_no_permission(self):
        from django.shortcuts import redirect
        from django.contrib import messages

        # Mensagem de erro (opcional)
        messages.error(self.request, "Você não tem permissão para acessar esta página.")
        
        # Redirecionar para uma página específica
        return redirect('/sem-permissao/')  # Customize para sua aplicação
