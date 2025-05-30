# app_tarefas/utils.py

from .models import TarefaModel

def buscar_tarefas_do_lancamento(tarefa_massa):
    return TarefaModel.objects.filter(
        massa=tarefa_massa,
    ).exclude(status='concluida')
