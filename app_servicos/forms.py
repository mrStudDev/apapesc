from django import forms
from .models import ServicoAssociadoModel, ServicoExtraAssociadoModel, ExtraAssociadoModel
from app_associados.models import AssociadoModel
from app_associacao.models import ReparticoesModel, AssociacaoModel
from django.forms import TextInput, Textarea
from django.core.exceptions import ValidationError
from app_servicos.models import StatusEtapaChoices
from app_finances.models import TipoServicoModel, EntradaFinanceira

class ExtraAssociadoForm(forms.ModelForm):
    class Meta:
        model = ExtraAssociadoModel
        fields = ['nome_completo', 'cpf', 'senha_gov', 'celular', 'content']
        widgets = {
            'nome_completo': forms.TextInput(attrs={
                'placeholder': 'Noeme Completo',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'data_inicial': forms.DateInput(attrs={
                'type': 'date',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }, format='%Y-%m-%d'),
            'cpf': forms.TextInput(attrs={
                'id': 'id_cpf',
                'placeholder': '000.000.000-00',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'oninput': 'mascaraCPF(this)',  # Chama a função de máscara para CPF
            }),            
            'senha_gov': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'celular': forms.TextInput(attrs={
                'placeholder': '(99)99999-9999',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'oninput': 'mascaraTelefone(this)',  # Chama a função de máscara para celular
            }),
            'content': forms.Textarea(attrs={
                'placeholder': 'Anotações',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm',
                'rows': 5,

            }), 
        }
        
        
class ServicoAssociadoForm(forms.ModelForm):
    status_etapa = forms.CharField(required=False, widget=forms.HiddenInput())  # 👈 Aqui é o pulo do gato

    class Meta:
        model = ServicoAssociadoModel
        exclude = ['associado', 'data_inicio', 'ultima_alteracao', 'criado_por']
        widgets = {
            'associacao': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'id': 'id_associacao_servico'
            }),
            'reparticao': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'id': 'id_reparticao_servico'
            }),
            'natureza_servico': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),            
            'tipo_servico': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3
            }),
        }

    def __init__(self, *args, associacao=None, editar_status=False, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['associacao'].queryset = AssociacaoModel.objects.all()

        # 🔹 Caso padrão: começa com queryset vazio para repartição
        self.fields['reparticao'].queryset = ReparticoesModel.objects.none()

        # 🔹 PRIORIDADE 1: Durante edição (instance já existente)
        if self.instance.pk and self.instance.associacao:
            self.fields['reparticao'].queryset = ReparticoesModel.objects.filter(
                associacao=self.instance.associacao
            )
            self.fields['associacao'].initial = self.instance.associacao

        # 🔹 PRIORIDADE 2: Durante POST (formulário sendo submetido)
        elif 'associacao' in self.data:
            try:
                assoc_id = int(self.data.get('associacao'))
                self.fields['reparticao'].queryset = ReparticoesModel.objects.filter(associacao_id=assoc_id)
                self.fields['associacao'].initial = AssociacaoModel.objects.get(id=assoc_id)
            except (ValueError, TypeError, AssociacaoModel.DoesNotExist):
                pass

        # 🔹 PRIORIDADE 3: Criando novo (via parâmetro da view)
        elif associacao:
            self.fields['reparticao'].queryset = ReparticoesModel.objects.filter(associacao=associacao)
            self.fields['associacao'].initial = associacao

        # 🔹 Mostrar status etapa no modo edição
        if editar_status:
            self.fields['status_etapa'].widget = forms.Select(
                choices=ServicoAssociadoModel._meta.get_field('status_etapa').choices,
                attrs={
                    'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
                }
            )


                
class ServicoExtraAssociadoForm(forms.ModelForm):
    class Meta:
        model = ServicoExtraAssociadoModel
        exclude = ['extra_associado', 'data_inicio', 'ultima_alteracao', 'criado_por']
        
        widgets = {
            'associacao': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'id': 'id_associacao_servico'
            }),
            'reparticao': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'id': 'id_reparticao_servico'
            }),
            'natureza_servico': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),              
            'tipo_servico': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'id': 'id_tipo_servico_servico'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3
            }),
            'status_etapa': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
        }
        
    def __init__(self, *args, **kwargs):
        associacao = kwargs.pop('associacao', None)
        super().__init__(*args, **kwargs)

        self.fields['associacao'].queryset = AssociacaoModel.objects.all()
        self.fields['reparticao'].queryset = ReparticoesModel.objects.none()

        if associacao:
            self.fields['reparticao'].queryset = ReparticoesModel.objects.filter(associacao=associacao)

        elif 'associacao' in self.data:
            try:
                assoc_id = int(self.data.get('associacao'))
                self.fields['reparticao'].queryset = ReparticoesModel.objects.filter(associacao_id=assoc_id)
            except (ValueError, TypeError):
                pass

        
        
    # Validação dos dígitos verificadores do CPF
    def calcular_digito(cpf_parcial):
        soma = sum(int(digito) * peso for digito, peso in zip(cpf_parcial, range(len(cpf_parcial) + 1, 1, -1)))
        resto = (soma * 10) % 11
        return resto if resto < 10 else 0

        if calcular_digito(numeros[:9]) != int(numeros[9]) or calcular_digito(numeros[:10]) != int(numeros[10]):
            raise ValidationError("CPF inválido.")

        return numeros

    def clean_celular(self):
        celular = self.cleaned_data.get('celular')
        # Remove caracteres não numéricos da string, como parênteses, hífens e espaços
        numeros = ''.join(c for c in celular if c.isdigit())
        # Verifique se o número tem 10 ou 11 dígitos
        if len(numeros) < 10 or len(numeros) > 11:
            raise ValidationError("O celular deve conter 10 ou 11 dígitos.")
        # Se você desejar, pode formatar o celular de volta ao formato desejado:
        celular_formatado = f"({numeros[:2]}){numeros[2:7]}-{numeros[7:]}"
        return celular_formatado