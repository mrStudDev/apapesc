from django.shortcuts import render
from django.http import Http404, FileResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, ListView, DetailView, UpdateView, View, DeleteView, TemplateView
from accounts.mixins import GroupPermissionRequiredMixin 
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Documento, TipoDocumentoModel, UpDocDriveModel
from app_associados.models import AssociadoModel
from app_associacao.models import IntegrantesModel, AssociacaoModel, ReparticoesModel
from app_servicos.models import ServicoExtraAssociadoModel, ExtraAssociadoModel
from app_tarefas.models import TarefaModel
from app_embarcacoes.models import EmbarcacoesModel
from .forms import DocumentoForm, TipoDocumentoForm
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
import io
import subprocess
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image
from django.contrib import messages
from django.utils import timezone
from django.utils.timezone import now
import datetime
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.utils.encoding import smart_str
import mimetypes
from .google_drive_integration import upload_to_drive
import fitz 
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator

# Create your views here.
class DocumentoUploadView(LoginRequiredMixin, GroupPermissionRequiredMixin, CreateView):
    model = Documento
    form_class = DocumentoForm
    template_name = 'app_documentos/upload_documento.html'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
        ]

    def dispatch(self, request, *args, **kwargs):
        tipo = kwargs.get('tipo')
        obj_id = kwargs.get('id')


        if tipo == 'associado':
            self.owner = get_object_or_404(AssociadoModel, id=obj_id)
        elif tipo == 'integrante':
            self.owner = get_object_or_404(IntegrantesModel, id=obj_id)
        elif tipo == 'associacao':
            self.owner = get_object_or_404(AssociacaoModel, id=obj_id)
        elif tipo == 'reparticao':
            self.owner = get_object_or_404(ReparticoesModel, id=obj_id)
        elif tipo == 'tarefa':
            self.owner = get_object_or_404(TarefaModel, id=obj_id)
        elif tipo == 'extraassociado':
            self.owner = get_object_or_404(ExtraAssociadoModel, id=obj_id)
        elif tipo == 'embarcacao':
            self.owner = get_object_or_404(EmbarcacoesModel, id=obj_id)
        elif tipo == 'repositorio':
            self.owner = 'repositorio_padrao'           
        else:
            raise Http404("Tipo de proprietário inválido.")

        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        tipos = request.POST.getlist('tipo_doc')
        nomes = request.POST.getlist('nome')
        arquivos = request.FILES.getlist('arquivo')
        descricoes = request.POST.getlist('descricao')

        enviados = 0
        total_antes = 0
        total_depois = 0
        mensagens_individuais = []

        for i in range(len(arquivos)):
            arquivo = arquivos[i]
            tipo_doc_id = tipos[i] if i < len(tipos) else ''
            nome_livre = nomes[i] if i < len(nomes) else ''
            descricao = descricoes[i] if i < len(descricoes) else ''

            doc = Documento(arquivo=arquivo)

            # Relacionamento com owner
            if isinstance(self.owner, AssociadoModel):
                doc.associado = self.owner
            elif isinstance(self.owner, IntegrantesModel):
                doc.integrante = self.owner
            elif isinstance(self.owner, AssociacaoModel):
                doc.associacao = self.owner
            elif isinstance(self.owner, ReparticoesModel):
                doc.reparticao = self.owner
            elif isinstance(self.owner, TarefaModel):
                doc.tarefa = self.owner
            elif isinstance(self.owner, ExtraAssociadoModel):
                doc.extra_associado = self.owner
            elif isinstance(self.owner, EmbarcacoesModel):
                doc.embarcacao = self.owner
            elif self.owner == 'repositorio_padrao':
                doc.repositorio_padrao = True


            # Tipo ou nome?
            if tipo_doc_id:
                tipo_doc = get_object_or_404(TipoDocumentoModel, id=tipo_doc_id)
                doc.tipo_doc = tipo_doc
            elif nome_livre:
                doc.nome = nome_livre
            else:
                messages.warning(request, f"❗ Documento {i+1} ignorado: nenhum tipo ou nome informado.")
                continue

            # Agora sim, seta a descrição
            doc.descricao = descricao

            doc.save()

            # Compressão
            path = doc.arquivo.path
            extensao = os.path.splitext(path)[-1].lower()
            tamanho_antes = os.path.getsize(path)

            comprimido = False
            if extensao in ['.jpg', '.jpeg', '.png']:
                comprimido = comprimir_imagem(path)
            elif extensao == '.pdf':
                comprimido = comprimir_pdf(path)

            tamanho_depois = os.path.getsize(path)
            total_antes += tamanho_antes
            total_depois += tamanho_depois
            enviados += 1

            if comprimido and tamanho_depois < tamanho_antes:
                economia = tamanho_antes - tamanho_depois
                mensagens_individuais.append(f"📄 Documento {i+1}: economia de {economia // 1024} KB")
            elif comprimido:
                mensagens_individuais.append(f"📄 Documento {i+1}: compressão aplicada, sem ganho real")
            else:
                mensagens_individuais.append(f"📄 Documento {i+1}: não foi possível comprimir")

        # Estatística geral
        economia = total_antes - total_depois
        economia_pct = (economia / total_antes * 100) if total_antes else 0
        economia_str = f"{economia // 1024} KB ({economia_pct:.1f}%)" if economia > 0 else "sem compressão aplicada"

        for msg in mensagens_individuais:
            messages.info(request, msg)

        messages.success(request, f"{enviados} documento(s) enviados. Economia total: {economia_str}")
        return HttpResponseRedirect(self.get_success_url())




    def form_valid(self, form):
        arquivo = form.cleaned_data.get("arquivo")

        if arquivo and arquivo.size > 104857600:  # 100MB
            form.add_error("arquivo", _("O arquivo excede o tamanho máximo permitido de 100MB."))
            return self.form_invalid(form)

        # Associar o documento ao proprietário correto
        if isinstance(self.owner, AssociadoModel):
            form.instance.associado = self.owner
        elif isinstance(self.owner, IntegrantesModel):
            form.instance.integrante = self.owner
        elif isinstance(self.owner, AssociacaoModel):
            form.instance.associacao = self.owner
        elif isinstance(self.owner, ReparticoesModel):
            form.instance.reparticao = self.owner
        elif isinstance(self.owner, TarefaModel):
            form.instance.tarefa = self.owner
        elif isinstance(self.owner, ExtraAssociadoModel):
            form.instance.extra_associado = self.owner  
        elif isinstance(self.owner, EmbarcacoesModel):
            form.instance.embarcacao = self.owner
        elif self.owner == 'repositorio_padrao':
            form.instance.repositorio_padrao = True

        # Validação extra: Garante que pelo menos o tipo ou o nome seja fornecido
        if not form.instance.tipo_doc and not form.instance.nome:
            raise ValueError("Você deve fornecer um nome ou selecionar um tipo para o documento.")

        return super().form_valid(form)

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owner'] = self.owner
        context['tipos_documento'] = TipoDocumentoModel.objects.order_by('tipo')
        return context

    def get_success_url(self):
        """
        Redireciona para a página de detalhes do proprietário correspondente.
        """
        if isinstance(self.owner, AssociadoModel):
            return reverse('app_associados:single_associado', kwargs={'pk': self.owner.pk})
        elif isinstance(self.owner, IntegrantesModel):
            return reverse('app_associacao:single_integrante', kwargs={'pk': self.owner.pk})
        elif isinstance(self.owner, AssociacaoModel):
            return reverse('app_associacao:single_associacao', kwargs={'pk': self.owner.pk})
        elif isinstance(self.owner, ReparticoesModel):
            return reverse('app_associacao:single_reparticao', kwargs={'pk': self.owner.pk})
        elif isinstance(self.owner, TarefaModel):
            return reverse('app_tarefas:single_tarefa', kwargs={'pk': self.owner.pk})
        elif isinstance(self.owner, ExtraAssociadoModel):
            return reverse('app_servicos:detail_extraassociado', kwargs={'pk': self.owner.pk})
        elif isinstance(self.owner, EmbarcacoesModel):
            return reverse('app_embarcacoes:single_embarcacao', kwargs={'pk':self.owner.pk})
        elif self.owner == 'repositorio_padrao':
            return reverse('app_documentos:repositorio_list')

    

def download_documento(request, pk):
    doc = get_object_or_404(Documento, pk=pk)

    if not doc.arquivo:
        raise Http404("Arquivo não encontrado.")

    # 🧠 Usa o nome salvo (e formatado no save()) como base
    nome_sem_extensao = doc.nome or "documento"
    extensao = os.path.splitext(doc.arquivo.name)[-1] or ".pdf"  # fallback seguro

    # 🔒 Slugify pra limpar caracteres especiais (pode manter espaços se quiser)
    nome_final = f"{slugify(nome_sem_extensao)}{extensao}"

    # Detecta o tipo MIME
    content_type, _ = mimetypes.guess_type(doc.arquivo.name)
    content_type = content_type or "application/octet-stream"

    # 📦 Retorna o arquivo com nome correto
    response = FileResponse(doc.arquivo.open('rb'), content_type=content_type)
    response["Content-Disposition"] = f'attachment; filename="{smart_str(nome_final)}"'

    return response

class TipoDocumentoCreateView(LoginRequiredMixin, GroupPermissionRequiredMixin, CreateView):
    model = TipoDocumentoModel
    template_name = 'app_documentos/create_tipo_documento.html'
    form_class = TipoDocumentoForm
    success_url = reverse_lazy('app_documentos:list_tipo_documento')  # Redireciona para a lista de tipos
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
        ]


class TipoDocumentoEditView(LoginRequiredMixin, GroupPermissionRequiredMixin, UpdateView):
    model = TipoDocumentoModel
    template_name = 'app_documentos/edit_tipo_doc.html'
    form_class = TipoDocumentoForm
    success_url = reverse_lazy('app_documentos:list_tipo_documento')

    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
    ]

    DOCUMENTOS_ESSENCIAIS = [
        'RG', 'RGP', 'NIT', 'CPF', 'CNH', 'CPF', 'TIE', 'CEI', 'CAEPF', 'Foto3x4', 
        'Comprovante Residência', 'Declaração Residência - MAPA',
        'Auto Declaração', 'Autorização de Acesso Gov Assinada',
        'Autorização de Uso de Imagem Assinada', 'Comprovante Seguro Defeso',
        'Ficha de Requerimento de Filiação Assinada', 'Título Eleitor',
        'Procuração Individual Ad Judicia Assinada', 'Procuração Individual Administrativa Assinada',
        'Licença Embarcação(Pesca)', 'Seguro DPEM', 'Protocolo RGP',
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tipo_documento = self.get_object()
        is_essencial = tipo_documento.tipo in self.DOCUMENTOS_ESSENCIAIS
        context.update({
            'is_essencial': is_essencial,
        })
        return context
        

class TipoDocListView(ListView):
    model = TipoDocumentoModel
    template_name = 'app_documentos/list_tipo_documento.html'
    context_object_name = 'tipos'
    ordering = ['tipo'] 
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
        ]
    
    def get_queryset(self):
        return TipoDocumentoModel.objects.all().order_by('tipo')  # Ordena por nome


# View para detalhes do documento
class DocumentoDetailView(LoginRequiredMixin, GroupPermissionRequiredMixin, DetailView):
    model = Documento
    template_name = 'app_documentos/documento_detail.html'
    context_object_name = 'documento'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['associado'] = self.object.associado
        context['integrante'] = self.object.integrante
        context['reparticao'] = self.object.reparticao
        context['tarefa'] = self.object.tarefa
        context['extraassociado'] = self.extraassociado
        context['embarcacao'] = self.object.embarcacao
        
        return context


class DocumentoDeleteView(LoginRequiredMixin, GroupPermissionRequiredMixin, View):
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
        ]

    def get(self, request, pk):
        """Renderiza a página de confirmação de exclusão."""
        documento = get_object_or_404(Documento, pk=pk)
        return render(request, 'app_documentos/delete_documento.html', {'documento': documento})

    def post(self, request, pk):
        """Deleta o documento após confirmação."""
        documento = get_object_or_404(Documento, pk=pk)

        # Determina o redirecionamento com base no proprietário do documento
        associado = documento.associado
        integrante = documento.integrante
        associcao = documento.associacao
        reparticao = documento.reparticao
        tarefa = documento.tarefa
        extra_associado = documento.extra_associado
        embarcacao = documento.embarcacao

        try:
            documento.delete()
            if associado:
                return redirect(reverse('app_associados:single_associado', kwargs={'pk': associado.pk}))
            elif integrante:
                return redirect(reverse('app_associacao:single_integrante', kwargs={'pk': integrante.pk}))
            elif associcao:
                return redirect(reverse('app_associacao:single_associacao', kwargs={'pk': associcao.pk}))
            elif reparticao:
                return redirect(reverse('app_associacao:single_reparticao', kwargs={'pk': reparticao.pk}))
            elif tarefa:
                return redirect(reverse('app_tarefas:single_tarefa', kwargs={'pk': tarefa.pk}))
            elif extra_associado:
                return redirect(reverse('app_servicos:single_servico_extra', kwargs={'pk': extra_associado.pk}))
            elif embarcacao:
                return redirect(reverse('app_embarcacoes:single_embarcacao', kwargs={'pk': embarcacao.pk}))
            else:
                return redirect('app_home:home')  # Fallback para a página inicial
        except Exception as e:
            return HttpResponse(f"Erro ao excluir o documento: {str(e)}", status=500)


@csrf_exempt
def criar_copia_pdf(request, pk):
    try:
        documento = Documento.objects.get(pk=pk)

        # Verifica se o documento está relacionado a um associado, integrante ou associação
        associado = getattr(documento, 'associado', None)
        integrante = getattr(documento, 'integrante', None)
        associacao = getattr(documento, 'associacao', None)
        reparticao = getattr(documento, 'reparticao', None)
        tarefa = getattr(documento, 'tarefa', None)
        extra_associado = getattr(documento, 'extra_associado', None)
        embarcacao = getattr(documento, 'embarcacao',None)

        if not associado and not integrante and not associacao and not reparticao and not tarefa and not extra_associado and not embarcacao:
            messages.error(request, 'Documento não associado a nenhum proprietário válido.')
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        # Determina o proprietário e o nome do documento
        if associado:
            owner_name = f"{associado.user.first_name} {associado.user.last_name}"
        elif integrante:
            owner_name = f"{integrante.user.first_name} {integrante.user.last_name}"
        elif associacao:
            owner_name = associacao.nome_fantasia
        elif reparticao:
            owner_name = reparticao.nome_reparticao
        elif tarefa:
            owner_name = tarefa.titulo
        elif extra_associado:
            owner_name = f"{extra_associado.nome_completo}"
        elif embarcacao:
            owner_name = embarcacao.nome_embarcacao

        # Verifica se o tipo está definido, caso contrário, usa o nome do documento
        tipo_nome = documento.tipo_doc.tipo if documento.tipo_doc else documento.nome
        if not tipo_nome:
            tipo_nome = "Documento_sem_tipo"

        pdf_name = f"{tipo_nome.replace(' ', '_')}_{owner_name.replace(' ', '_')}_copia.pdf"
        pdf_path = os.path.join(settings.MEDIA_ROOT, "documentos", pdf_name)

        # Cria o diretório se não existir
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

        # Lógica para arquivos de imagem
        if documento.arquivo.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=A4)
            a4_width, a4_height = A4

            with Image.open(documento.arquivo.path) as img:
                img_width, img_height = img.size
                aspect_ratio = img_width / img_height

                # Calcula o tamanho da imagem para caber na página A4 com margens
                margin = 50  # Margem de 50 unidades em todos os lados
                max_width = a4_width - 2 * margin
                max_height = a4_height - 2 * margin

                if aspect_ratio > 1:
                    width = min(max_width, img_width)
                    height = width / aspect_ratio
                else:
                    height = min(max_height, img_height)
                    width = height * aspect_ratio

                # Ajusta se exceder o tamanho máximo permitido
                if width > max_width:
                    width = max_width
                    height = width / aspect_ratio
                if height > max_height:
                    height = max_height
                    width = height * aspect_ratio

                x = (a4_width - width) / 2  # Centraliza horizontalmente
                y = (a4_height - height) / 2  # Centraliza verticalmente

                p.drawImage(documento.arquivo.path, x, y, width=width, height=height)

            p.showPage()
            p.save()

            # Salva o PDF no disco
            buffer.seek(0)
            with open(pdf_path, 'wb') as f:
                f.write(buffer.read())

        # Lógica para arquivos DOCX
        elif documento.arquivo.name.lower().endswith('.docx'):
            # Caminho completo do arquivo DOCX
            docx_path = documento.arquivo.path

            # Comando para converter o DOCX para PDF usando o LibreOffice
            command = [
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', os.path.dirname(pdf_path),
                docx_path
            ]

            # Executa o comando
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Verifica se a conversão foi bem-sucedida
            if result.returncode != 0:
                messages.error(request, f'Erro na conversão do documento: {result.stderr.decode("utf-8")}')
                return redirect(request.META.get('HTTP_REFERER', '/'))
            
            # O LibreOffice salva o PDF com o mesmo nome do arquivo DOCX, mas com extensão .pdf
            original_pdf_name = os.path.splitext(os.path.basename(docx_path))[0] + '.pdf'
            original_pdf_path = os.path.join(os.path.dirname(pdf_path), original_pdf_name)

            # Renomeia o PDF para o nome desejado
            os.rename(original_pdf_path, pdf_path)

        else:
            messages.error(request, 'Formato de arquivo não suportado.')
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        # Formata a data atual


        # Salva o PDF no banco de dados sem duplicar o nome do proprietário

        documento_copia = Documento.objects.create(
            associado=associado if associado else None,
            integrante=integrante if integrante else None,
            associacao=associacao if associacao else None,
            reparticao=reparticao if reparticao else None,
            tarefa=tarefa if tarefa else None,
            extra_associado=extra_associado if extra_associado else None,
            embarcacao=embarcacao if embarcacao else None,
            tipo_doc=documento.tipo_doc,
            nome=documento.nome,
            arquivo=f"documentos/{pdf_name}",
            descricao=f"Cópia PDF - Documento gerado automaticamente - {documento.nome}"
        )
        

        # Define a mensagem de sucesso
        messages.success(request, 'Cópia em PDF do documento, foi criada com sucesso!')

        # Redireciona para a página do proprietário
        if associado:
            return redirect(reverse('app_associados:single_associado', kwargs={'pk': associado.pk}))
        elif integrante:
            return redirect(reverse('app_associacao:single_integrante', kwargs={'pk': integrante.pk}))
        elif associacao:
            return redirect(reverse('app_associacao:single_associacao', kwargs={'pk': associacao.pk}))
        elif reparticao:
            return redirect(reverse('app_associacao:single_reparticao', kwargs={'pk': reparticao.pk}))
        elif tarefa:
            return redirect(reverse('app_tarefas:single_tarefa', kwargs={'pk': tarefa.pk}))
        elif extra_associado:
            return redirect(reverse('app_servicos:detail_extraassociado', kwargs={'pk': extra_associado.pk}))
        elif embarcacao:
            return redirect(reverse('app_embarcacoes:single_embarcacao', kwargs={'pk': embarcacao.pk}))

    except Documento.DoesNotExist:
        messages.error(request, 'Documento não encontrado.')
        return redirect(request.META.get('HTTP_REFERER', '/'))
    except Exception as e:
        messages.error(request, f'Erro ao criar a cópia do documento: {str(e)}')
        return redirect(request.META.get('HTTP_REFERER', '/'))

#================================================================================


# app_documentos
# UPLOAD TO DRIVE FOLDER
def upload_docs_view(request, associado_id):
    associado = get_object_or_404(AssociadoModel, id=associado_id)
    tipos_documento = TipoDocumentoModel.objects.order_by('tipo')

    if request.method == 'POST':
        arquivos = request.FILES.getlist('arquivo')
        tipos = request.POST.getlist('tipo_documento')
        enviados = 0
        total_antes = 0
        total_depois = 0
        mensagens_individuais = []  # <- Aqui estava faltando inicialização!

        for i, arquivo in enumerate(arquivos):
            tipo_id = tipos[i]
            tipo = TipoDocumentoModel.objects.get(id=tipo_id)

            upload = UpDocDriveModel.objects.create(
                associado=associado,
                tipo_documento=tipo,
                arquivo=arquivo
            )

            nome_extensao = os.path.splitext(arquivo.name)[-1]
            nome_final = f"{tipo.tipo} - {associado.user.get_full_name()} - {now().strftime('%Y-%m-%d_%H-%M')}{nome_extensao}"
            upload.nome_final = nome_final
            upload.save()

            folder_id = associado.drive_folder_id.split('?')[0]
            path = upload.arquivo.path
            extensao = os.path.splitext(path)[-1].lower()

            tamanho_antes = os.path.getsize(path)
            print(f"📁 Iniciando compressão para: {upload.arquivo.name} ({extensao})")
            print(f"🔸 Tamanho antes: {tamanho_antes} bytes")

            # Compressão
            comprimido = False
            if extensao in ['.jpg', '.jpeg', '.png']:
                comprimido = comprimir_imagem(path)
            elif extensao == '.pdf':
                comprimido = comprimir_pdf(path)

            tamanho_depois = os.path.getsize(path)
            print(f"🔻 Tamanho depois: {tamanho_depois} bytes")

            total_antes += tamanho_antes
            total_depois += tamanho_depois

            if comprimido and tamanho_depois < tamanho_antes:
                economia = tamanho_antes - tamanho_depois
                mensagens_individuais.append(
                    f"📁 '{nome_final}': economia de {economia // 1024} KB"
                )
            elif comprimido:
                mensagens_individuais.append(
                    f"📁 '{nome_final}': compressão aplicada, mas sem redução significativa"
                )
            else:
                mensagens_individuais.append(
                    f"📁 '{nome_final}': não foi possível aplicar compressão"
                )

            try:
                upload_to_drive(path, nome_final, folder_id)
                enviados += 1
            except Exception as e:
                messages.error(request, f"Erro ao enviar '{arquivo.name}': {str(e)}")

        # 🔹 Estatísticas Finais
        economia_bytes = total_antes - total_depois
        economia_percentual = (economia_bytes / total_antes * 100) if total_antes else 0
        economia_str = f"{economia_bytes // 1024} KB ({economia_percentual:.1f}%)" if economia_bytes > 0 else "sem compressão aplicada"

        # 🔹 Exibe todas as mensagens após o loop
        for msg in mensagens_individuais:
            messages.info(request, msg)

        messages.success(request, f"{enviados} documento(s) enviados com sucesso ao Google Drive. Economia total: {economia_str}")
        return redirect('app_associados:single_associado', pk=associado_id)

    return render(request, 'app_documentos/upload_to_drive.html', {
        'associado': associado,
        'tipos_documento': tipos_documento
    })

    

def comprimir_imagem(path, qualidade=75):
    try:
        img = Image.open(path)
        if img.format in ['JPEG', 'JPG', 'PNG']:
            img = img.convert('RGB')
            img.save(path, optimize=True, quality=qualidade)
            print(f"✔️ Imagem comprimida: {path}")
            return True
        else:
            print(f"🟡 Formato não suportado: {img.format}")
    except Exception as e:
        print(f"❌ Erro ao comprimir imagem: {e}")
    return False


def comprimir_pdf(path):
    try:
        temp_path = path.replace(".pdf", "_compressed.pdf")
        doc = fitz.open(path)
        doc.save(temp_path, deflate=True, garbage=4)
        doc.close()

        # Substitui o original pelo comprimido
        os.replace(temp_path, path)

        print(f"✔️ PDF comprimido com sucesso: {path}")
        return True
    except Exception as e:
        print(f"❌ Erro ao comprimir PDF: {e}")
        return False
    
    
#==========================================================================



# Repositório de Documentos e Mensagens
#RepositórioDocumentos
class RepositorioUpListView(LoginRequiredMixin, GroupPermissionRequiredMixin, View):
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Diretor(a) da Associação',
    ]
    template_name = 'app_documentos/repositorio_upload_list.html'
    form_class = DocumentoForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        documentos = Documento.objects.filter(repositorio_padrao=True).order_by('-data_upload')
        return render(request, self.template_name, {
            'form': form,
            'documentos': documentos
        })

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.repositorio_padrao = True
            doc.save()

            # Compressão
            path = doc.arquivo.path
            extensao = os.path.splitext(path)[-1].lower()
            if extensao in ['.jpg', '.jpeg', '.png']:
                comprimir_imagem(path)
            elif extensao == '.pdf':
                comprimir_pdf(path)

            messages.success(request, "📥 Documento enviado ao repositório com sucesso!")
            return redirect('app_documentos:repositorio')  # Define esse nome no `urls.py`

        documentos = Documento.objects.filter(repositorio_padrao=True).order_by('-data_upload')
        return render(request, self.template_name, {
            'form': form,
            'documentos': documentos
        })    

        
class DocumentoRepositorioDeleteView(LoginRequiredMixin, GroupPermissionRequiredMixin, DeleteView):
    model = Documento
    success_url = reverse_lazy('app_documentos:repositorio_list')
    group_required = ['Superuser', 'Admin da Associação', 'Diretor(a) da Associação']


# Mensagens padrão - página
class MensagensRepositorioView(LoginRequiredMixin, GroupPermissionRequiredMixin, TemplateView):
    template_name = 'app_documentos/repositorio_msg.html'
    group_required = ['Superuser', 'Admin da Associação', 'Auxiliar da Repartição']
