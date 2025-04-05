from django.views.generic import ListView, DetailView
from .models import EspecieMarinhaModel, ReinoModel, FiloModel, UsoCulinarioModel
from django.db.models import Q
from django.shortcuts import get_object_or_404




class ListEspecieMarinhaView(ListView):
    model = EspecieMarinhaModel
    template_name = 'app_especies_maritimas/list_especies.html'
    context_object_name = 'especies'
    paginate_by = 20
    ordering = ['nome_cientifico']

    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.GET.get('q')
        grupo = self.request.GET.get('grupo')
        reino = self.request.GET.get('reino')
        filo = self.request.GET.get('filo')
        familia = self.request.GET.get('familia')

        if search_term:
            queryset = queryset.filter(
                Q(nome_comum__icontains=search_term) |
                Q(nome_cientifico__icontains=search_term)
            )

        if grupo:
            queryset = queryset.filter(grupo_biologico__nome=grupo)

        if reino:
            queryset = queryset.filter(reino_id=reino)

        if filo:
            queryset = queryset.filter(filo_id=filo)

        if familia:
            queryset = queryset.filter(familia=familia)

        return queryset.select_related('reino', 'filo', 'grupo_biologico',)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        queryset = self.get_queryset()

        context.update({
            'total_especies': queryset.count(),
            'search_term': self.request.GET.get('q', ''),
            'reinos': ReinoModel.objects.all(),
            'filos': FiloModel.objects.all(),

            # Pegando famílias distintas no formato (valor, label)
            'familias': queryset.values_list('familia', 'familia').distinct().order_by('familia'),

            'selected_reino': self.request.GET.get('reino', ''),
            'selected_filo': self.request.GET.get('filo', ''),
            'selected_familia': self.request.GET.get('familia', ''),
        })
        return context





class SingleEspecieMarinhaView(DetailView):
    model = EspecieMarinhaModel
    template_name = 'app_especies_maritimas/single_especie.html'
    context_object_name = 'especie'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        return get_object_or_404(
            EspecieMarinhaModel.objects.select_related(
                'reino', 'filo', 'grupo_biologico'
            ).prefetch_related(
                'habitat',
                'status_conservacao',
                'nomes_comuns',
                'referencias_bibliograficas',
                'distribuicao_geografica',
                'ameacas',
                'receitas'
            ),
            slug=self.kwargs['slug']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        especie = context['especie']

        context.update({
            'titulo_pagina': f"{especie.nome_comum} ({especie.nome_cientifico})",
            'meta_descricao': f"Informações sobre {especie.nome_comum}: {especie.descricao[:160]}" if especie.descricao else "",
            'has_imagem_principal': bool(especie.imagem_principal),
            'imagens': especie.imagens.all(),
            'status_conservacao': especie.status_conservacao.filter(sistema='iucn').first(),
            'nomes_comuns': especie.nomes_comuns.all(),
            'distribuicoes': especie.distribuicao_geografica.all(),
            'ameacas': especie.ameacas.all(),
            'receitas': especie.receitas.all()[:3]
        })

        return context


class SingleReceitaView(DetailView):
    model = UsoCulinarioModel
    template_name = 'app_especies_maritimas/single_receita.html'
    context_object_name = 'receita'