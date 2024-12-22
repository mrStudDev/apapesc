from django.db import models
from django.utils import timezone
from app_associados.models import AssociadoModel



class TipoDocumentoModel(models.Model):
    tipo = models.CharField(max_length=300, verbose_name="Nome do Tipo de Documento")

    def __str__(self):
        return self.tipo


class Documento(models.Model):
    associado = models.ForeignKey(
        'app_associados.AssociadoModel',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='documentos'
    )
    integrante = models.ForeignKey(
        'app_associacao.IntegrantesModel',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='documentos'
    )
    tipo_doc = models.ForeignKey(
        'TipoDocumentoModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tipo de Documento"
    )
    nome = models.CharField(max_length=300, verbose_name="Nome do Documento", blank=True)
    arquivo = models.FileField(upload_to='documentos/', verbose_name="Arquivo")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    data_upload = models.DateTimeField(auto_now_add=True, verbose_name="Data de Upload")

    def save(self, *args, **kwargs):
        # Inicializa a data atual formatada
        data_str = timezone.now().strftime('%Y-%m-%d')

        # Determina o proprietário (associado ou integrante) e usa nome e sobrenome
        if self.associado:
            nome_proprietario = f"{self.associado.user.first_name} {self.associado.user.last_name}"
        elif self.integrante:
            nome_proprietario = f"{self.integrante.user.first_name} {self.integrante.user.last_name}"
        else:
            raise ValueError("Documento deve estar associado a um Associado ou Integrante.")

        # Define o nome do documento
        if self.tipo_doc:
            self.nome = f"{self.tipo_doc.tipo} - {nome_proprietario} - {data_str}"
        elif self.nome:  # Usa o nome fornecido se não houver tipo_doc
            self.nome = f"{self.nome} - {nome_proprietario} - {data_str}"
        else:
            # Define um nome padrão caso nenhum tipo ou nome sejam fornecidos
            self.nome = f"Documento sem tipo - {nome_proprietario} - {data_str}"

        super().save(*args, **kwargs)


    def __str__(self):
        if self.associado:
            return f"{self.nome} - Associado: {self.associado.user.first_name} {self.associado.user.last_name}"
        elif self.integrante:
            return f"{self.nome} - Integrante: {self.integrante.user.first_name} {self.integrante.user.last_name}"
        else:
            return f"{self.nome} - Sem proprietário definido"

