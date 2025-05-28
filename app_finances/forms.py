from django import forms
from app_finances.models import AnuidadeModel
from app_finances.models import (
    TipoDespesaModel,
    DespesaAssociacaoModel,
    TipoServicoModel,
    EntradaFinanceira,
    )
from app_associacao.models import ReparticoesModel, AssociacaoModel
from decimal import Decimal, InvalidOperation  # Import Decimal and InvalidOperation


class AnuidadeForm(forms.ModelForm):
    class Meta:
        model = AnuidadeModel
        fields = ['ano', 'valor_anuidade']
        widgets = {
            'ano': forms.NumberInput(attrs={
                'placeholder': 'Digite o Ano (Ex: 2025)',
                'class': 'border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm'
            }),
            'valor_anuidade': forms.TextInput(attrs={
                'placeholder': 'Valor da Anuidade (Ex: 250.00) Use o ponto para separar os centavos.',
                'class': 'border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm',
            }),
        }


# 🔹 Formulário para cadastrar/editar tipos de despesas
class TipoDespesaForm(forms.ModelForm):
    class Meta:
        model = TipoDespesaModel
        fields = ['nome', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Nome do Tipo de Despesa'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Descrição opcional'
            }),
        }



class DespesaAssociacaoForm(forms.ModelForm):
    class Meta:
        model = DespesaAssociacaoModel
        exclude = ['registrado_por'] 
        fields = '__all__'
        widgets = {
            'associacao': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'onchange': 'carregarReparticoes(this.value)'
            }),
            'reparticao': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'tipo_despesa': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'valor': forms.NumberInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Valor da despesa'
            }),
            'data_vencimento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }, format='%Y-%m-%d'),
            'numero_nota_fiscal': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Número da Nota Fiscal (opcional)',
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Descrição da despesa'
            }),
            'pago': forms.CheckboxInput(attrs={  # ✅ Adicionamos um checkbox!
                'class': 'form-checkbox h-5 w-5 text-blue-600',
            }),
            'comprovante_nota': forms.FileInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Comprovante da despesa (opcional)',
            }),
            'data_upload_comprovante': forms.DateInput(attrs={
                'type': 'datetime-local',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }, format='%Y-%m-%dT%H:%M'),
            'data_lancamento': forms.DateInput(attrs={
                'type': 'datetime-local',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }, format='%Y-%m-%dT%H:%M'),       
        }

    def __init__(self, *args, user=None, **kwargs):

        super().__init__(*args, **kwargs)  # Chama super() apenas uma vez
        self.user = user  # Guarda o usuário autenticado

        # Filtra repartições com base na associação
        if 'associacao' in self.data:
            associacao_id = self.data.get('associacao')
            if associacao_id:
                self.fields['reparticao'].queryset = ReparticoesModel.objects.filter(associacao_id=associacao_id)
            else:
                self.fields['reparticao'].queryset = ReparticoesModel.objects.none()
        elif self.instance.pk:  # Se a despesa já existir
            self.fields['reparticao'].queryset = ReparticoesModel.objects.filter(associacao=self.instance.associacao)
        else:
            self.fields['reparticao'].queryset = ReparticoesModel.objects.none()
            

# 🔹 Formulário para cadastrar/editar Tipos de Serviço
class TipoServicoForm(forms.ModelForm):
    class Meta:
        model = TipoServicoModel
        fields = ['nome', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Nome do Tipo de Serviço'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Descrição opcional'
            }),
        }

# 🔹 Formulário para cadastrar/editar Entradas da Associação
class EntradaFinanceiraForm(forms.ModelForm):

    class Meta:
        model = EntradaFinanceira
        fields = [
            'associacao', 
            'reparticao',
            'tipo_servico',
            'descricao',
            'valor_total', 
            'forma_pagamento',                       
            'parcelamento',
            'data_criacao',

        ]
        widgets = {
            'associacao': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'onchange': 'carregarReparticoes(this.value)'  # ✅ Chama a função para carregar repartições dinamicamente
            }),
            'reparticao': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'tipo_servico': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Descrição da entrada'
            }),            
            'valor_total': forms.NumberInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Valor da entrada'
            }),
            'data_criacao': forms.DateInput(attrs={
                'type': 'datetime-local',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }, format='%Y-%m-%dT%H:%M'),  
            'forma_pagamento': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'parcelamento': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),       
            "status_pagamento": forms.TextInput(attrs={"readonly": "readonly"
            }),  # 🔥 Agora não editável                        
        }

    def __init__(self, *args, user=None, associacao=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        self.fields['associacao'].queryset = AssociacaoModel.objects.all()
        self.fields['tipo_servico'].queryset = TipoServicoModel.objects.all()
        
        # Ajusta o queryset das repartições
        if 'associacao' in self.data:
            associacao_id = self.data.get('associacao')
            if associacao_id:
                self.fields['reparticao'].queryset = ReparticoesModel.objects.filter(associacao_id=associacao_id)
            else:
                self.fields['reparticao'].queryset = ReparticoesModel.objects.none()
        elif associacao:
            self.fields['reparticao'].queryset = ReparticoesModel.objects.filter(associacao=associacao)
        elif self.instance.pk:
            self.fields['reparticao'].queryset = ReparticoesModel.objects.filter(associacao=self.instance.associacao)
        else:
            self.fields['reparticao'].queryset = ReparticoesModel.objects.none()

            
    def clean(self):
        cleaned_data = super().clean()
        
        # 🔹 Verifica se a entrada já existe
        if not self.instance.pk:
            return cleaned_data  # ✅ Se for uma nova entrada, não valida parcelas!

        parcela_id = self.data.get("parcela_id")
        valor_pagamento = self.data.get("valor_pagamento")

        # 🔹 Garante que `valor_pagamento` nunca seja None
        if not valor_pagamento:
            valor_pagamento = "0.00"

        try:
            # 🔹 Converte `valor_pagamento` para Decimal apenas se for diferente de None
            valor_pagamento = Decimal(str(valor_pagamento).replace(",", "."))
        except (ValueError, InvalidOperation, AttributeError):
            raise forms.ValidationError("Valor do pagamento inválido. Informe um número válido.")

        # 🔹 Se o usuário digitou um valor, mas não selecionou parcela, exibir erro
        if not parcela_id and valor_pagamento > 0:
            raise forms.ValidationError("Você deve selecionar uma parcela para pagamento.")

        cleaned_data["valor_pagamento"] = valor_pagamento  # 🔥 Garante que o campo seja atualizado
        return cleaned_data

    
    def clean_valor_pagamento(self):
        valor_pagamento = self.cleaned_data.get("valor_pagamento")

        # 🔹 Se for None, define como "0.00" para evitar erro
        if valor_pagamento is None:
            return Decimal('0.00')  
        
        # 🔹 Garante que é Decimal e faz conversão segura
        if isinstance(valor_pagamento, str):
            valor_pagamento = Decimal(valor_pagamento.replace(",", "."))

        return valor_pagamento



        