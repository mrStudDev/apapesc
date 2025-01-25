import os
from django.db import models
from django.conf import settings
from pathlib import Path

from pathlib import Path

def upload_to_declaracao_residencia(instance, filename):
    file_path = os.path.join('pdf', 'declaracao_residencia.pdf')
    full_path = Path(settings.MEDIA_ROOT) / file_path

    # Verifica se o arquivo existe antes de tentar removê-lo
    if full_path.exists():
        try:
            full_path.unlink()  # Remove o arquivo existente
        except PermissionError:
            print(f"Permissão negada ao tentar remover {full_path}")
        except Exception as e:
            print(f"Erro ao remover {full_path}: {e}")

    return file_path



def upload_to_declaracao_filiacao(instance, filename):
    return f'pdf/declaracao_filiacao.pdf'

def upload_to_declaracao_atividade_pesqueira(instance, filename):
    return f'pdf/declaracao_atividade_pesqueira.pdf'

def upload_to_declaracao_hipossuficiencia(instance, filename):
    return f'pdf/declaracao_hipossuficiencia.pdf'

def upload_to_procuracao_juridica(instance, filename):
    return f'pdf/procuracao_juridica.pdf'

def upload_to_termo_compromisso(instance, filename):
    return f'pdf/termo_compromisso.pdf'

def upload_to_certificado_associado_legal(instance, filename):
    return f'pdf/certificado_associado_legal.pdf'


class DeclaracaoResidenciaModel(models.Model):
    pdf_base = models.FileField(
        upload_to=upload_to_declaracao_residencia,
        verbose_name="PDF Base para Declaração de Residência",
        help_text="Substituirá o arquivo base atual para a declaração de residência."
    )
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    def save(self, *args, **kwargs):
        # Substituir o arquivo existente se for necessário
        if self.pk:
            old_instance = DeclaracaoResidenciaModel.objects.get(pk=self.pk)
            if old_instance.pdf_base and old_instance.pdf_base != self.pdf_base:
                # Remove o arquivo anterior
                if os.path.isfile(old_instance.pdf_base.path):
                    os.remove(old_instance.pdf_base.path)

        super().save(*args, **kwargs)

    def __str__(self):
        return "Declaração de Residência"



class DeclaracaoFiliacaoModel(models.Model):
    pdf_base = models.FileField(
        upload_to=upload_to_declaracao_filiacao,
        verbose_name="PDF Base para Declaração de Filiação",
        help_text="Substituirá o arquivo base atual para a declaração de filiação."
    )
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    def save(self, *args, **kwargs):
        # Substituir o arquivo existente se for necessário
        if self.pk:
            old_instance = DeclaracaoFiliacaoModel.objects.get(pk=self.pk)
            if old_instance.pdf_base and old_instance.pdf_base != self.pdf_base:
                # Remove o arquivo anterior
                if os.path.isfile(old_instance.pdf_base.path):
                    os.remove(old_instance.pdf_base.path)

        super().save(*args, **kwargs)

    def __str__(self):
        return "Declaração de Filiação"


class DeclaracaoAtividadePesqueiraModel(models.Model):
    pdf_base = models.FileField(
        upload_to=upload_to_declaracao_atividade_pesqueira,
        verbose_name="PDF Base para Declaração de Atividade Pesqueira",
        help_text="Substituirá o arquivo base atual para a declaração de Atividade Pesqueira."
    )
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    def save(self, *args, **kwargs):
        # Substituir o arquivo existente se for necessário
        if self.pk:
            old_instance = DeclaracaoAtividadePesqueiraModel.objects.get(pk=self.pk)
            if old_instance.pdf_base and old_instance.pdf_base != self.pdf_base:
                # Remove o arquivo anterior
                if os.path.isfile(old_instance.pdf_base.path):
                    os.remove(old_instance.pdf_base.path)

        super().save(*args, **kwargs)

    def __str__(self):
        return "Declaração de Atividade Pesqueira"


class DeclaracaoHipossuficienciaModel(models.Model):
    pdf_base = models.FileField(
        upload_to=upload_to_declaracao_hipossuficiencia,
        verbose_name="PDF Base para Declaração de Hipossuficiência",
        help_text="Substituirá o arquivo base atual para a declaração de Atividade Pesqueira."
    )
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    def save(self, *args, **kwargs):
        # Substituir o arquivo existente se for necessário
        if self.pk:
            old_instance = DeclaracaoHipossuficienciaModel.objects.get(pk=self.pk)
            if old_instance.pdf_base and old_instance.pdf_base != self.pdf_base:
                # Remove o arquivo anterior
                if os.path.isfile(old_instance.pdf_base.path):
                    os.remove(old_instance.pdf_base.path)

        super().save(*args, **kwargs)
        
    def __str__(self):
        return "Declaração de Hipossuficiência"

class ProcuracaoJuridicaModel(models.Model):
    pdf_base = models.FileField(
        upload_to=upload_to_procuracao_juridica,
        verbose_name="PDF Base para Procuração Jurídica",
        help_text="Substituirá o arquivo base atual para a procuração jurídica."
    )
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    def save(self, *args, **kwargs):
        # Substituir o arquivo existente se for necessário
        if self.pk:
            old_instance = ProcuracaoJuridicaModel.objects.get(pk=self.pk)
            if old_instance.pdf_base and old_instance.pdf_base != self.pdf_base:
                # Remove o arquivo anterior
                if os.path.isfile(old_instance.pdf_base.path):
                    os.remove(old_instance.pdf_base.path)

        super().save(*args, **kwargs)
        
    def __str__(self):
        return "Procuração Jurídica"

class TermoCompromissoModel(models.Model):
    pdf_base = models.FileField(
        upload_to=upload_to_termo_compromisso,
        verbose_name="PDF Base para Termo de Compromisso",
        help_text="Substituirá o arquivo base atual para o termo de compromisso."
    )
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    def save(self, *args, **kwargs):
        # Substituir o arquivo existente se for necessário
        if self.pk:
            old_instance = TermoCompromissoModel.objects.get(pk=self.pk)
            if old_instance.pdf_base and old_instance.pdf_base != self.pdf_base:
                # Remove o arquivo anterior
                if os.path.isfile(old_instance.pdf_base.path):
                    os.remove(old_instance.pdf_base.path)

        super().save(*args, **kwargs)
        
    def __str__(self):
        return "Termo de Compromisso"

class CertificadoAssociadoLegalModel(models.Model):
    pdf_base = models.FileField(
        upload_to=upload_to_certificado_associado_legal,
        verbose_name="PDF Base para Certificado de Associado Legal",
        help_text="Substituirá o arquivo base atual para o certificado de associado legal."
    )
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    def save(self, *args, **kwargs):
        # Substituir o arquivo existente se for necessário
        if self.pk:
            old_instance = CertificadoAssociadoLegalModel.objects.get(pk=self.pk)
            if old_instance.pdf_base and old_instance.pdf_base != self.pdf_base:
                # Remove o arquivo anterior
                if os.path.isfile(old_instance.pdf_base.path):
                    os.remove(old_instance.pdf_base.path)

        super().save(*args, **kwargs)
        
    def __str__(self):
        return "Certificado de Associado Legal"
    
            