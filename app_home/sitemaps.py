from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse

class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.9

    def items(self):
        return [
            'app_home:home',
            'app_home:sobre',
            'app_home:contact-us',
            'app_home:associe_se',

            ]  # Ajuste as rotas aqui

    def location(self, item):
        return reverse(item)
