from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
from .models import AssociadoModel, ProfissoesModel
import bleach
from app_associacao.models import AssociacaoModel, ReparticoesModel, MunicipiosModel


class AssociadoForm(forms.ModelForm):
    class Meta:
        model = AssociadoModel
        fields = '__all__'
     
        
class AssociadoForm(forms.ModelForm):
    class Meta:
        model = AssociadoModel
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
        
        # Se o formulário tiver uma instância associada a um usuário, define o e-mail inicial
        if self.instance and self.instance.user:
            self.fields['email'].initial = self.instance.user.email
        elif user:
            # Caso um novo associado, tenta usar o usuário passado explicitamente
            self.fields['email'].initial = user.email
        # Tornar o campo e-mail somente leitura
        self.fields['email'].widget.attrs['readonly'] = True
        
        # Personalize os campos de espécie e quantidade, se necessário
        for i in range(1, 5):
            self.fields[f'especie{i}'].widget.attrs.update({
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            })
            self.fields[f'quantidade{i}'].widget.attrs.update({
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Digite a quantidade em Kg',
                'step': '0.01'
            })
        
        # Configuração de campos adicionais
        self.fields['profissao'].queryset = ProfissoesModel.objects.all().order_by('nome')
        self.fields['content'].widget = forms.Textarea(attrs={'class': 'hidden-editor'})
        self.fields['estado_civil'].choices = sorted(
            self.fields['estado_civil'].choices,
            key=lambda choice: choice[1]
        )
        # Configurações de Associação
        self.fields['associacao'].queryset = AssociacaoModel.objects.all()
        self.fields['associacao'].label_from_instance = lambda obj: obj.nome_fantasia

        # Configurações de Repartições
        self.fields['reparticao'].queryset = ReparticoesModel.objects.all()
        self.fields['reparticao'].label_from_instance = lambda obj: obj.nome_reparticao

        # Configurações de Municípios
        self.fields['municipio_circunscricao'].queryset = MunicipiosModel.objects.all()
        self.fields['municipio_circunscricao'].label_from_instance = lambda obj: obj.municipio

    def clean_user(self):
        # Não permitir alteração do campo `user` na edição
        if self.instance.pk:
            return self.instance.user
        return self.cleaned_data.get('user')
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if not cpf:
            return cpf  # Retorna sem validação adicional se CPF estiver vazio

        # Verifica se o CPF já existe em outra instância
        queryset = AssociadoModel.objects.filter(cpf=cpf)
        if self.instance and self.instance.pk:
            # Exclui o próprio objeto da verificação
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise forms.ValidationError("Este CPF já está cadastrado em outro associado.")
        return cpf
                
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

    def clean_celular_correspondencia(self):
        celular_correspondencia = self.cleaned_data.get('celular_correspondencia')
        # Remove caracteres não numéricos da string, como parênteses, hífens e espaços
        numeros = ''.join(c for c in celular_correspondencia if c.isdigit())
        # Verifique se o número tem 10 ou 11 dígitos
        if len(numeros) < 10 or len(numeros) > 11:
            raise ValidationError("O celular deve conter 10 ou 11 dígitos.")
        # Se você desejar, pode formatar o celular de volta ao formato desejado:
        celular_correspondencia_formatado = f"({numeros[:2]}){numeros[2:7]}-{numeros[7:]}"
        return celular_correspondencia_formatado    

    def clean_data_nascimento(self):
        data = self.cleaned_data.get('data_nascimento')
        if not data:
            return None  # Permita valores nulos
        return data

    def clean_rg_data_emissao(self):
        data = self.cleaned_data.get('rg_data_emissao')
        if not data:
            return None  # Permita valores nulos
        return data 
    
    def clean_rgp_data_emissao(self):
        data = self.cleaned_data.get('rgp_data_emissao')
        if not data:
            return None  # Permita valores nulos
        return data
    
    def clean_primeiro_registro(self):
        data = self.cleaned_data.get('primeiro_registro')
        if not data:
            return None  # Permita valores nulos
        return data

    def clean_ctps_data_emissao(self):
        data = self.cleaned_data.get('ctps_data_emissao')
        if not data:
            return None  # Permita valores nulos
        return data 
    
    def clean_cnh_data_emissao(self):
        data = self.cleaned_data.get('cnh_data_emissao')
        if not data:
            return None  # Permita valores nulos
        return data 
        
    def clean_data_emissao(self):
            
        data = self.cleaned_data.get('data_emissao')
        if not data:
            return None  # Permita valores nulos
        return data

    def clean_cep(self):
        cep = self.cleaned_data.get('cep')
        # Se o CEP não for preenchido, retorna None ou string vazia
        if not cep:
            return cep  # Retorna o valor original sem validar
        
        # Remove caracteres não numéricos
        numeros = ''.join(c for c in cep if c.isdigit())
        
        # Verifica se o CEP tem exatamente 8 dígitos
        if len(numeros) != 8:
            raise ValidationError("O CEP deve conter exatamente 8 dígitos.")
        
        # Retorna o CEP formatado com o hífen
        return f"{numeros[:5]}-{numeros[5:]}"
    