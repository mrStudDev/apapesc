from django.contrib.auth.mixins import UserPassesTestMixin

class GroupPermissionRequiredMixin(UserPassesTestMixin):
    group_required = None

    def test_func(self):
        user = self.request.user
        if self.group_required:
            return user.groups.filter(name=self.group_required).exists() or user.is_superuser
        return False