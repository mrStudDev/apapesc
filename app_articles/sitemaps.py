from django.contrib.sitemaps import Sitemap
from .models import ArticlesModel, CategoryArticlesModel, TagArticlesModel

class ArticleSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return ArticlesModel.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.last_updated

class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return CategoryArticlesModel.objects.all()

class TagSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return TagArticlesModel.objects.all()