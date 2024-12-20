from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
from .models import(
    ApapescModel,
    IntegrantesModel,
    ReparticoesModel,
    MunicipiosModel,
    CargosModel,
    
)

from django.core.exceptions import ValidationError


class ApapescForm(forms.ModelForm):
    class Meta:
        model = ApapescModel
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['apapesc'].queryset = ApapescModel.objects.all()
        # Ajustar o campo apapesc para exibir o nome_fantasia
        self.fields['diretores'].queryset = ApapescModel.objects.all()


    def clean_data_abertura(self):
        data = self.cleaned_data.get('data_abertura')
        if not data:
            return None  # Permita valores nulos
        return data

    def clean_data_encerramento(self):
        data = self.cleaned_data.get('data_encerramento')
        if not data:
            return None  # Permita valores nulos
        return data
    
    def clean_cep(self):
        cep = self.cleaned_data.get('cep')
        # Se o CEP não for preenchido, retorna None ou string vazia
        if not cep:
            return cep  # Retorna o valor original sem validar
        # Remove o hífen e valida se o valor tem apenas dígitos
        numeros = ''.join(c for c in cep if c.isdigit())
        if len(numeros) != 8:
            raise ValidationError("O CEP deve conter exatamente 8 dígitos.")

        return numeros  # Retorna apenas os números do celular
    
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

class ReparticaoForm(forms.ModelForm):
    class Meta:
        model = ReparticoesModel
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajustar o campo apapesc para exibir o nome_fantasia
        self.fields['apapesc'].queryset = ApapescModel.objects.all()
        self.fields['apapesc'].label_from_instance = lambda obj: obj.nome_fantasia
        self.fields['municipio_sede'].queryset = MunicipiosModel.objects.all()
        self.fields['delegado'].queryset = IntegrantesModel.objects.all()
        self.fields['municipios_circunscricao'].queryset = MunicipiosModel.objects.all()
        self.fields['nome_reparticao'].queryset = ReparticoesModel.objects.all()
        
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
    
    def clean_cep(self):
        cep = self.cleaned_data.get('cep')
        # Se o CEP não for preenchido, retorna None ou string vazia
        if not cep:
            return cep  # Retorna o valor original sem validar
        # Remove o hífen e valida se o valor tem apenas dígitos
        numeros = ''.join(c for c in cep if c.isdigit())
        if len(numeros) != 8:
            raise ValidationError("O CEP deve conter exatamente 8 dígitos.")

        return numeros  # Retorna apenas os números do celular
    
    def clean_data_abertura(self):
        data = self.cleaned_data.get('data_abertura')
        if not data:
            return None  # Permita valores nulos
        return data

    def clean_data_encerramento(self):
        data = self.cleaned_data.get('data_encerramento')
        if not data:
            return None  # Permita valores nulos
        return data

class IntegranteForm(forms.ModelForm):
    class Meta:
        model = IntegrantesModel
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['integrantes'].queryset = IntegrantesModel.objects.all()
        # Ajustar o campo apapesc para exibir o nome_fantasia
        self.fields['cargo'].queryset = CargosModel.objects.all()
        self.fields['nome_reparticao'].queryset = ReparticoesModel.objects.all()
        
    # Validação dos dígitos verificadores do CPF
    def calcular_digito(cpf_parcial):
        soma = sum(int(digito) * peso for digito, peso in zip(cpf_parcial, range(len(cpf_parcial) + 1, 1, -1)))
        resto = (soma * 10) % 11
        return resto if resto < 10 else 0

        if calcular_digito(numeros[:9]) != int(numeros[9]) or calcular_digito(numeros[:10]) != int(numeros[10]):
            raise ValidationError("CPF inválido.")

        return numeros
    
    def clean_cep(self):
        cep = self.cleaned_data.get('cep')
        # Se o CEP não for preenchido, retorna None ou string vazia
        if not cep:
            return cep  # Retorna o valor original sem validar
        # Remove o hífen e valida se o valor tem apenas dígitos
        numeros = ''.join(c for c in cep if c.isdigit())
        if len(numeros) != 8:
            raise ValidationError("O CEP deve conter exatamente 8 dígitos.")

        return numeros
    def clean_data_nascimento(self):
        data = self.cleaned_data.get('data_nascimento')
        if not data:
            return None  # Permita valores nulos
        return data

    def clean_data_emissao(self):
        data = self.cleaned_data.get('data_emissao')
        if not data:
            return None  # Permita valores nulos
        return data 
    
    def clean_data_entrada(self):
        data = self.cleaned_data.get('data_entrada')
        if not data:
            return None  # Permita valores nulos
        return data

    def clean_data_saida(self):
        data = self.cleaned_data.get('data_saida')
        if not data:
            return None  # Permita valores nulos
        return data
    
class MunicipioForm(forms.ModelForm):
    class Meta:
        model = MunicipiosModel
        fields = '__all__'
        widgets = {
            'municipio': forms.TextInput(attrs={
                'placeholder': 'Digite o nome do Município',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700',
            }),
            'uf': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),                        
        }


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

    
    def clean_cep(self):
        cep = self.cleaned_data.get('cep')
        # Se o CEP não for preenchido, retorna None ou string vazia
        if not cep:
            return cep  # Retorna o valor original sem validar
        # Remove o hífen e valida se o valor tem apenas dígitos
        numeros = ''.join(c for c in cep if c.isdigit())
        if len(numeros) != 8:
            raise ValidationError("O CEP deve conter exatamente 8 dígitos.")

        return numeros  # Retorna apenas os números do celular

