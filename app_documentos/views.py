from django.shortcuts import render
from django.http import Http404
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, ListView, DetailView, UpdateView, View
from accounts.mixins import GroupPermissionRequiredMixin 
from .models import Documento, TipoDocumentoModel
from app_associados.models import AssociadoModel
from app_associacao.models import IntegrantesModel, AssociacaoModel, ReparticoesModel
from app_tarefas.models import TarefaModel
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
import datetime


# Create your views here.

class DocumentoUploadView(GroupPermissionRequiredMixin, CreateView):
    model = Documento
    form_class = DocumentoForm
    template_name = 'app_documentos/upload_documento.html'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente',
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
        else:
            raise Http404("Tipo de proprietário inválido.")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
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

        # Validação extra: Garante que pelo menos o tipo ou o nome seja fornecido
        if not form.instance.tipo_doc and not form.instance.nome:
            raise ValueError("Você deve fornecer um nome ou selecionar um tipo para o documento.")

        return super().form_valid(form)

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owner'] = self.owner
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


class TipoDocumentoCreateView(CreateView):
    model = TipoDocumentoModel
    template_name = 'app_documentos/create_tipo_documento.html'
    form_class = TipoDocumentoForm
    success_url = reverse_lazy('app_documentos:list_tipo_documento')  # Redireciona para a lista de tipos
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
        ]    

class TipoDocListView(ListView):
    model = TipoDocumentoModel
    template_name = 'app_documentos/list_tipo_documento.html'
    context_object_name = 'tipos'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
        ]
    
    def get_queryset(self):
        return TipoDocumentoModel.objects.all().order_by('tipo')  # Ordena por nome


# View para detalhes do documento
class DocumentoDetailView(GroupPermissionRequiredMixin, DetailView):
    model = Documento
    template_name = 'app_documentos/documento_detail.html'
    context_object_name = 'documento'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['associado'] = self.object.associado
        context['integrante'] = self.object.integrante
        context['reparticao'] = self.object.reparticao
        context['tarefa'] = self.object.tarefa
        return context



class DocumentoDeleteView(GroupPermissionRequiredMixin, View):
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente',
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

        if not associado and not integrante and not associacao and not reparticao and not tarefa:
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

    except Documento.DoesNotExist:
        messages.error(request, 'Documento não encontrado.')
        return redirect(request.META.get('HTTP_REFERER', '/'))
    except Exception as e:
        messages.error(request, f'Erro ao criar a cópia do documento: {str(e)}')
        return redirect(request.META.get('HTTP_REFERER', '/'))
