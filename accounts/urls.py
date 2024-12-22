from django.urls import path
from .views import custom_login_redirect

app_name = 'accounts'

urlpatterns = [
    path('custom-login-redirect/', custom_login_redirect, name='custom_login_redirect'),
    # Outras rotas do seu app
]
