from email.policy import default
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import random
from django.utils.text import slugify


class CategoryArticlesModel(models.Model):
    name = models.CharField(max_length=155)
    description = models.CharField(max_length=160)
    slug = models.SlugField()

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('app_articles:category_articles', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class TagArticlesModel(models.Model):
    name = models.CharField(max_length=155)
    description = models.CharField(max_length=160)
    slug = models.SlugField()

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('app_articles:tags_articles', kwargs={'slug': self.slug})


class ArticlesModel(models.Model):
    title = models.CharField(max_length=60)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    image_source = models.TextField(  # Campo para a fonte da imagem
        max_length=500, 
        blank=True, 
        null=True, 
        verbose_name="Fonte da Imagem"
    )   
    meta_title = models.CharField(max_length=60)
    author = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    category = models.ForeignKey(CategoryArticlesModel, null=True, blank=True, on_delete=models.SET_NULL, related_name='articles')
    content = models.TextField(blank=True, null=True)
    keywords = models.CharField(max_length=255)   
    meta_description = models.TextField(max_length=160)
    tags = models.ManyToManyField('TagArticlesModel', blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)
    is_vip = models.BooleanField(default=False, verbose_name="É VIP")
    old_url = models.SlugField(blank=True, null=True)
    slug = models.SlugField(blank=True, unique=True)
    last_updated = models.DateTimeField(auto_now=True)
    research_sources = models.TextField( # Campo para fontes de pesquisa
        blank=True, 
        null=True, 
        verbose_name="Fontes de Pesquisa"
    )
    code = models.PositiveIntegerField(unique=True, blank=True, null=True)

    
    def generate_unique_code(self):
        code = random.randint(100000, 999999)
        while ArticlesModel.objects.filter(code=code).exists():
            code = random.randint(100000, 999999)
        return code

    def save(self, *args, **kwargs):
        # Gera um código único se não existir
        if not self.code:
            self.code = self.generate_unique_code()
        # Gera um slug a partir do título se o slug não existir
        if not self.slug:
            self.slug = slugify(self.title)
        super(ArticlesModel, self).save(*args, **kwargs)


    def __str__(self):
        return f"{self.title} | {self.author}"


    def get_absolute_url(self):
        return reverse('app_articles:article-single', kwargs={'slug': self.slug})

