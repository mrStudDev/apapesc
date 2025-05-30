# app_tarefas/utils.py

from app_associados.models import AssociadoModel
from .models import ReapsAnualModel, ReapsAssociadoItem
from .models import TarefaModel


# Tarefas Recadastramento
def buscar_tarefas_do_lancamento(tarefa_massa):
    return TarefaModel.objects.filter(
        massa=tarefa_massa,
    ).exclude(status='concluida')


# Reaps Anual
def criar_lancamento_reaps(user, ano=None):
    from datetime import date
    if not ano:
        ano = date.today().year

    reaps = ReapsAnualModel.objects.create(
        ano=ano,
        criado_por=user
    )

    associados = AssociadoModel.objects.filter(
        status__in=['Associado Lista Ativo(a)', 'Associado Lista Aposentado(a)']
    )

    for associado in associados:
        ReapsAssociadoItem.objects.create(
            reaps=reaps,
            associado=associado,
            status='PENDENTE'
        )

    return reaps