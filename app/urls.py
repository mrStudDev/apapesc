"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static


from django.contrib.sitemaps.views import sitemap
from django.views.generic import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage

from app_articles.sitemaps import ArticleSitemap, CategorySitemap
from app_home.sitemaps import StaticViewSitemap
from django.conf.urls.static import static


sitemaps = {
    'articles': ArticleSitemap(),
    'categories': CategorySitemap(),
    'static': StaticViewSitemap(),
}


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('', include('app_home.urls', namespace='app_home')),
    path('manager/', include('app_manager.urls', namespace='app_manager')),
    path('associacao/', include('app_associacao.urls', namespace='app_associacao')),
    path('associados/', include('app_associados.urls', namespace='app_associados')),
    path('documentos/', include('app_documentos.urls', namespace='app_documentos')),
    path('automacoes/', include('app_automacoes.urls', namespace='app_automacoes')),
    path('tarefas/', include('app_tarefas.urls', namespace='app_tarefas')),
    path('artigos/', include('app_articles.urls', namespace='app_articles')),
    path('financas/', include('app_finances.urls', namespace='app_finances')),
    path('servicos/', include('app_servicos.urls', namespace='app_servicos')),
    path('embarcacoes/', include('app_embarcacoes.urls', namespace='app_embarcacoes')),
    path('licencas/', include('app_licencas.urls', namespace='app_licencas')),
    path('especies/', include('app_especies_maritimas.urls', namespace='app_especies_maritimas')),
    path('beneficios/', include('app_beneficios.urls', namespace='app_beneficios')),
    

    # Rotas de SEO
    path('robots.txt', RedirectView.as_view(url=staticfiles_storage.url('seo/robots.txt')), name='robots_file'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('google2e294c64b6641554.html', RedirectView.as_view(url=staticfiles_storage.url('seo/google2e294c64b6641554.html')), name='google_verification'),
    #path('BingSiteAuth.xml', RedirectView.as_view(url=staticfiles_storage.url('seo/BingSiteAuth.xml')), name='bing_auth_file'),
    #path('fbe920112a7946ea91b904e0ebf284d3.txt', RedirectView.as_view(url=staticfiles_storage.url('seo/fbe920112a7946ea91b904e0ebf284d3.txt')), name='bing_indexnow_file'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)