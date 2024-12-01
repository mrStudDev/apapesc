
from django.urls import path
from . import views

#from common.permissions import custom_login_redirect

app_name = 'app_home'

urlpatterns = [
    path('', views.HomeView, name='home'),
]
