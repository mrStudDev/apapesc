from django import forms
from .models import Documento, TipoDocumentoModel
from app_associados.models import AssociadoModel
from app_associacao.models import IntegrantesModel

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo_doc'].queryset = TipoDocumentoModel.objects.all().order_by('tipo')
        self.fields['tipo_doc'].label = "Tipo do Documento"
        self.fields['arquivo'].widget.attrs.update({'class': 'file-input'})
        self.fields['descricao'].widget.attrs.update({'placeholder': 'Adicione uma descrição para o documento...'})
        self.fields['nome'].label = "Nome do Documento (Preencha apenas se não houver Tipo)"
        self.fields['nome'].required = False
        self.fields['tipo_doc'].required = False
        
    def clean_arquivo(self):
        arquivo = self.cleaned_data.get('arquivo')

        # Verifica se o arquivo é maior que 5MB
        if arquivo.size > 100 * 1024 * 1024:
            raise forms.ValidationError("O arquivo não pode ser maior que 100MB.")
        
        return arquivo


class TipoDocumentoForm(forms.ModelForm):
    class Meta:
        model = TipoDocumentoModel
        fields = ['tipo']
        labels = {
            'tipo': 'Tipo de Documento',
        }
        widgets = {
            'tipo': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Digite o nome do tipo de documento',
            }),
        }