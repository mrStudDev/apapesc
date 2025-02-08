
from django.urls import path
from . import views
from .views import (
    HomeView,
    LeadMessagesListView,
    SobreNosView,
    Associese_View,
    ListContactMessagesView,
    ViewContactMessageView
    )
#from common.permissions import custom_login_redirect

app_name = 'app_home'

urlpatterns = [
    path('', views.HomeView, name='home'),
    path('mensagens/', LeadMessagesListView.as_view(), name='list_mensagens'),
    path('mensagens/<int:pk>/delete/', views.delete_lead_message, name='delete_lead_message'),
    path('sobre/', views.SobreNosView.as_view(), name='sobre'),
    path('contato/', views.contact_view, name='contact-us'),
    path('associe-se/', views.Associese_View.as_view(), name='associe_se'),
    path('mensagens-contatos/', ListContactMessagesView.as_view(), name='list_contact_messages'),
    path('mensagens-contato/<int:pk>/', ViewContactMessageView.as_view(), name='view_message'),
]

