import datetime
from django import forms
from django.contrib.auth.models import Group
from django.utils import timezone
from app_associacao.models import IntegrantesModel
from app_tarefas.models import TarefaModel
from django.contrib.auth.models import User
from app_associados.models import AssociadoModel


class TarefaForm(forms.ModelForm):
    associado = forms.ModelChoiceField(
        queryset=AssociadoModel.objects.all(),
        required=False,
        label="Associado",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    responsaveis = forms.ModelMultipleChoiceField(
        queryset=IntegrantesModel.objects.all(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'size': '15',
            }
        ),
        label="Responsáveis"
    )
    class Meta:
        model = TarefaModel
        fields = '__all__'
        widgets = {
            'criado_por': forms.HiddenInput(), 
            'titulo': forms.TextInput(attrs={
                'placeholder': 'Título da tarefa',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-green-600 font-bold leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'descricao': forms.TextInput(attrs={
                'placeholder': 'Breve descricao',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-green-600 font-bold leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'data_criacao': forms.DateInput(attrs={
                'type': 'date',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500'
            }, format='%Y-%m-%d'),
            'data_limite': forms.DateInput(attrs={
                'type': 'date',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500'
            }, format='%Y-%m-%d'),
            'hora_limite': forms.TimeInput(attrs={
                'type': 'time',
                'step': 1,
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500'
            }, format='%H:%M:%S'),
            'status': forms.TextInput(attrs={
                'placeholder': 'Digite o nome completo',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-green-600 font-bold leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),  
            'categoria': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),  
            'prioridade': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),                                 
            
            'responsaveis': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            

        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'criado_por' in self.fields:
            self.fields['criado_por'].required = False

        # Ajusta o queryset corretamente para AssociadoModel, ordenando pelo nome do usuário
        self.fields['associado'].queryset = AssociadoModel.objects.select_related('user').order_by('user__first_name', 'user__last_name')

        # Exibe o nome completo do usuário associado no campo de seleção
        self.fields['associado'].label_from_instance = lambda obj: obj.user.get_full_name() or obj.user.username
        
                # Caso o associado já esteja definido, tornar o campo readonly
        if self.initial.get('associado'):
            self.fields['associado'].widget.attrs['readonly'] = True