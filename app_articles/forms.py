from django import forms
from .models import ArticlesModel, TagArticlesModel, CategoryArticlesModel

class ArticleCreateForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=TagArticlesModel.objects.all(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'size': '15',
            }
        ),
        label="Tags"
    )    
    class Meta:
        model = ArticlesModel
        exclude = ['author']
        fields = ['title', 'meta_title', 'image', 'image_source', 'category', 'content', 'keywords', 'meta_description', 'research_sources', 'is_published', 'is_vip', ]
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Título do Artigo',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm'
            }),
            'meta_title': forms.TextInput(attrs={
                'placeholder': 'Título (repetir título) - Meta',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),  
            'image': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm',
                'id': 'image-upload',  # Opcional, útil para estilização ou testes
            }),
            'image_source': forms.TextInput(attrs={
                'placeholder': 'URL da Fonte da Imagem',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-3 px-4 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm'
            }),            
            'category': forms.Select(attrs={
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),                    
            'content': forms.Textarea(attrs={
                'placeholder': 'Escreva o conteúdo do artigo aqui...',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm',
                'rows': 10,
                'id': 'editor',
            }),
            'keywords': forms.TextInput(attrs={
                'placeholder': 'Palavras Chave (separe por vírgula)',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),  
            'meta_description': forms.TextInput(attrs={
                'placeholder': 'Breve Descrição - Meta',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }), 
            'research_sources': forms.Textarea(attrs={
                'placeholder': 'Fontes de Pesquisa',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm',
                'rows': 10,
                'id': 'font-editor',
            }),            
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-blue-600 transition duration-150 ease-in-out',
                'id': 'is-published-checkbox',  # Opcional, útil para testes ou estilização adicional
            }),
            'is_vip': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-blue-600 transition duration-150 ease-in-out',
                'id': 'is-vip-checkbox',  # Opcional, útil para testes ou estilização adicional
            }),                                  
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['tags'].initial = self.instance.tags.all()

    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        # Se quiser obrigar a ter pelo menos 1, tudo bem.
        if not tags:
            raise forms.ValidationError("Selecione ao menos uma tag.")
        return tags
    
    
    
class CategoryArticlesForm(forms.ModelForm):
    class Meta:
        model = CategoryArticlesModel
        exclude = ['slug']
        fields = ['name', 'description', 'slug']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Nome da Categoria',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm'
            }),
            'description': forms.TextInput(attrs={
                'placeholder': 'Descrição da Categoria',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm'
            }),
            'slug': forms.TextInput(attrs={
                'placeholder': 'Slug da Categoria',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm'
            }),
        }


class TagArticlesForm(forms.ModelForm):
    class Meta:
        model = TagArticlesModel
        exclude = ['slug']
        fields = ['name', 'description', 'slug']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Nome da Tag',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm'
            }),
            'description': forms.TextInput(attrs={
                'placeholder': 'Descrição da Tag',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm'
            }),
            'slug': forms.TextInput(attrs={
                'placeholder': 'Slug da Tag',
                'class': 'appearance-none border border-gray-300 rounded-md w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm'
            }),
        }
