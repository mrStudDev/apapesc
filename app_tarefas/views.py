from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.utils.timezone import now
from django.contrib.auth.models import User
from accounts.mixins import GroupPermissionRequiredMixin 
from django.contrib.auth.models import Group


class TarefaListView(ListView):
    pass

class TarefaCreateView(CreateView):
    pass