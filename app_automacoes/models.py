import os
from django.db import models
from django.conf import settings
from pathlib import Path

# Funções de upload para os arquivos PDF
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
    file_path = os.path.join('pdf', 'declaracao_filiacao.pdf')
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

def upload_to_declaracao_atividade_pesqueira(instance, filename):
    file_path = os.path.join('pdf', 'declaracao_atividade_pesqueira.pdf')
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

def upload_to_declaracao_hipossuficiencia(instance, filename):
    file_path = os.path.join('pdf', 'declaracao_hipossuficiencia.pdf')
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

def upload_to_procuracao_juridica(instance, filename):
    file_path = os.path.join('pdf', 'procuracao_juridica.pdf')
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

def upload_to_termo_compromisso(instance, filename):
    file_path = os.path.join('pdf', 'termo_compromisso.pdf')
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

def upload_to_certificado_associado_legal(instance, filename):
    file_path = os.path.join('pdf', 'certificado_associado_legal.pdf')    
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

def upload_to_recibo_anuidade(instance, filename):
    file_path = os.path.join('pdf', 'recibo_anuidade.pdf')
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


def upload_to_cobranca_anuidade(instance, filename):
    file_path = os.path.join('pdf', 'cobranca_anuidades.pdf')
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


def upload_to_recibo_servico_extra(instance, filename):
    file_path = os.path.join('pdf', 'recibo_servico_extra.pdf')
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

def upload_to_carteirinha_apapesc(instance, filename):
    file_path = os.path.join('pdf', 'carteirinha_apapesc.pdf')
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

def upload_to_procuracao_administrativa(instance, filename):
    file_path = os.path.join('pdf', 'procuracao_administrativa.pdf')
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

def uoload_to_autorizacao_direito_imagem(instance, filename):
    file_path = os.path.join('pdf', 'autorizacao_direito_imagem.pdf')
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

def upload_to_autorizacao_acesso_gov(instance, filename):
    file_path = os.path.join('pdf', 'autorizacao_acesso_gov.pdf')
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

def upload_to_declaracao_desfiliacao(instance, filename):
    file_path = os.path.join('pdf', 'declaracao_desfiliacao.pdf')
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


def upload_to_direitos_deveres(instance, filename):
    file_path = os.path.join('pdf', 'direitos_deveres.pdf')
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

    
# Modelos para armazenar os arquivos PDF
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
    

class ReciboAnuidadeModel(models.Model):
    pdf_base = models.FileField(
        upload_to=upload_to_recibo_anuidade,
        verbose_name="PDF Base para Recibo Anuidade",
        help_text="Substituirá o arquivo base atual para a Recibos/Anuidades."
    )
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    def save(self, *args, **kwargs):
        # Substituir o arquivo existente se for necessário
        if self.pk:
            old_instance = ReciboAnuidadeModel.objects.get(pk=self.pk)
            if old_instance.pdf_base and old_instance.pdf_base != self.pdf_base:
                # Remove o arquivo anterior
                if os.path.isfile(old_instance.pdf_base.path):
                    os.remove(old_instance.pdf_base.path)

        super().save(*args, **kwargs)
        
    def __str__(self):
        return "Recibo Anuidade" 

class CobrancaAnuidadeModel(models.Model):
    pdf_base = models.FileField(
        upload_to=upload_to_cobranca_anuidade,
        verbose_name="PDF Base para Cobrança Anuidade",
        help_text="Substituirá o arquivo base atual para a Cobrança/Anuidades."
    )
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    def save(self, *args, **kwargs):
        # Substituir o arquivo existente se for necessário
        if self.pk:
            old_instance = CobrancaAnuidadeModel.objects.get(pk=self.pk)
            if old_instance.pdf_base and old_instance.pdf_base != self.pdf_base:
                # Remove o arquivo anterior
                if os.path.isfile(old_instance.pdf_base.path):
                    os.remove(old_instance.pdf_base.path)

        super().save(*args, **kwargs)
    def __str__(self):
        return "Cobrança Anuidade"
    

class ReciboServicoExtraModel(models.Model):
    pdf_base = models.FileField(
        upload_to=upload_to_recibo_servico_extra,
        verbose_name="PDF Base para Recibo Serviço Extra",
        help_text="Substituirá o arquivo base atual para a Recibos/Serviço Extra."
    )
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    def save(self, *args, **kwargs):
        # Substituir o arquivo existente se for necessário
        if self.pk:
            old_instance = ReciboServicoExtraModel.objects.get(pk=self.pk)
            if old_instance.pdf_base and old_instance.pdf_base != self.pdf_base:
                # Remove o arquivo anterior
                if os.path.isfile(old_instance.pdf_base.path):
                    os.remove(old_instance.pdf_base.path)

        super().save(*args, **kwargs)
    def __str__(self):
        return "Recibo Serviço Extra"

class CarteirinhaAssociadoModel(models.Model):
    pdf_base = models.FileField(
        upload_to=upload_to_carteirinha_apapesc,
        verbose_name="PDF Base para Carteirinha do Associado",
        help_text="Substituirá o arquivo base atual para a Carteirinha do Associado."
    )
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    def save(self, *args, **kwargs):
        # Substituir o arquivo existente se for necessário
        if self.pk:
            old_instance = CarteirinhaAssociadoModel.objects.get(pk=self.pk)
            if old_instance.pdf_base and old_instance.pdf_base != self.pdf_base:
                # Remove o arquivo anterior
                if os.path.isfile(old_instance.pdf_base.path):
                    os.remove(old_instance.pdf_base.path)

        super().save(*args, **kwargs)
        
    def __str__(self):
        return "Carteirinha do Associado"
    
class ProcuracaoAdministrativaModel(models.Model):
    pdf_base = models.FileField(
        upload_to=upload_to_procuracao_administrativa,
        verbose_name="PDF Base para Procuração Administrativa",
        help_text="Substituirá o arquivo base atual para a procuração administrativa."
    )
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    def save(self, *args, **kwargs):
        # Substituir o arquivo existente se for necessário
        if self.pk:
            old_instance = ProcuracaoAdministrativaModel.objects.get(pk=self.pk)
            if old_instance.pdf_base and old_instance.pdf_base != self.pdf_base:
                # Remove o arquivo anterior
                if os.path.isfile(old_instance.pdf_base.path):
                    os.remove(old_instance.pdf_base.path)

        super().save(*args, **kwargs)
        
    def __str__(self):
        return "Procuração Administrativa"


class AutorizacaoDireitoImagemModel(models.Model):
    pdf_base = models.FileField(
        upload_to=uoload_to_autorizacao_direito_imagem,
        verbose_name="PDF Base para Autorização de Direito de Imagem",
        help_text="Substituirá o arquivo base atual para a autorização de direito de imagem."
    )
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    def save(self, *args, **kwargs):
        # Substituir o arquivo existente se for necessário
        if self.pk:
            old_instance = AutorizacaoDireitoImagemModel.objects.get(pk=self.pk)
            if old_instance.pdf_base and old_instance.pdf_base != self.pdf_base:
                # Remove o arquivo anterior
                if os.path.isfile(old_instance.pdf_base.path):
                    os.remove(old_instance.pdf_base.path)

        super().save(*args, **kwargs)
        
    def __str__(self):
        return "Autorização de Direito de Imagem"

class AutorizacaoAcessoGovModel(models.Model):
    pdf_base = models.FileField(
        upload_to=upload_to_autorizacao_acesso_gov,
        verbose_name="PDF Base para Autorização de Acesso ao Gov",
        help_text="Substituirá o arquivo base atual para a autorização de acesso ao Gov."
    )
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    def save(self, *args, **kwargs):
        # Substituir o arquivo existente se for necessário
        if self.pk:
            old_instance = AutorizacaoAcessoGovModel.objects.get(pk=self.pk)
            if old_instance.pdf_base and old_instance.pdf_base != self.pdf_base:
                # Remove o arquivo anterior
                if os.path.isfile(old_instance.pdf_base.path):
                    os.remove(old_instance.pdf_base.path)

        super().save(*args, **kwargs)
        
    def __str__(self):
        return "Autorização de Acesso ao Gov"    
    
class DeclaracaoDesfiliacaoModel(models.Model):
    pdf_base = models.FileField(
        upload_to=upload_to_declaracao_desfiliacao,
        verbose_name="PDF Base para Declaração de Desfiliação",
        help_text="Substituirá o arquivo base atual para a declaração de desfiliação."
    )
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    def save(self, *args, **kwargs):
        # Substituir o arquivo existente se for necessário
        if self.pk:
            old_instance = DeclaracaoDesfiliacaoModel.objects.get(pk=self.pk)
            if old_instance.pdf_base and old_instance.pdf_base != self.pdf_base:
                # Remove o arquivo anterior
                if os.path.isfile(old_instance.pdf_base.path):
                    os.remove(old_instance.pdf_base.path)

        super().save(*args, **kwargs)
        
    def __str__(self):
        return "Declaração de Desfiliação"
    
class DireitosDeveres(models.Model):
    pdf_base = models.FileField(
        upload_to=upload_to_direitos_deveres,
        verbose_name="PDF Base para Regramentos Direitos e Deveres",
        help_text="Substituirá o arquivo base atual para Regramentos Direitos e Deveres."
    )
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    def save(self, *args, **kwargs):
        # Substituir o arquivo existente se for necessário
        if self.pk:
            old_instance = DireitosDeveres.objects.get(pk=self.pk)
            if old_instance.pdf_base and old_instance.pdf_base != self.pdf_base:
                # Remove o arquivo anterior
                if os.path.isfile(old_instance.pdf_base.path):
                    os.remove(old_instance.pdf_base.path)

        super().save(*args, **kwargs)
        
    def __str__(self):
        return "Declaração de Desfiliação"    