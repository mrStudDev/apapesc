# settings_production
import os
from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(os.path.join(Path(__file__).resolve().parent.parent, '.env'))

DJANGO_SETTINGS_MODULE = env("DJANGO_SETTINGS_MODULE", default="app.settings_production")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY", default="chave-padrao-insegura")


DEBUG = env.bool("DEBUG", default=False)
# REAL 34.55.106.64
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS_PROD", default=["apapesc.com", "www.apapesc.com", "35.226.35.185",])


# Application definition

INSTALLED_APPS = [
    # Aplicativos de autenticação
    'accounts', # App Accounts
    'allauth',
    'allauth.account',
    # Aplicativos de Padrão do Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Aplicativos Externos
    'django_cleanup.apps.CleanupConfig',
    'django.contrib.sitemaps', # Sitemap do Django
    'django.contrib.humanize',
    
    # Apps 
    'app_home',
    'app_manager',
    'app_associacao',
    'app_associados',
    'app_documentos',
    'app_automacoes',
    'app_tarefas',
    'app_articles',
    'app_finances',
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Middleware do allauth
    'allauth.account.middleware.AccountMiddleware',    
]

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'accounts.context_processors.group_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# Database Produção
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME_PROD'),
        'USER': env('DB_USER_PROD'),
        'PASSWORD': env('DB_PASSWORD_PROD'),
        'HOST': env('DB_HOST_PROD'),
        'PORT': env('DB_PORT_PROD'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = 'media/'



# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Autenticação padrão do Django
    'allauth.account.auth_backends.AuthenticationBackend',  # Backend do django-allauth
]

# Envia e-mails para o console (apenas para desenvolvimento)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Configuração do Allauth
ACCOUNT_FORMS = {
    'signup': 'accounts.forms.CustomSignupForm',
    'login': 'accounts.forms.CustomLoginForm',
    }

ACCOUNT_AUTHENTICATION_METHOD = "username_email"  # Login por email ou username
ACCOUNT_USERNAME_REQUIRED = True  # Nome de usuário obrigatório
ACCOUNT_EMAIL_REQUIRED = True  # Email obrigatório
ACCOUNT_UNIQUE_EMAIL = True  # Email deve ser único
ACCOUNT_SIGNUP_FIELDS = ['username', 'first_name', 'last_name', 'email']  # Campos obrigatórios no formulário de cadastro

                     
# Sessão Logins
#ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/custom-login-redirect/'  # Redireciona após logout
LOGIN_REDIRECT_URL = '/accounts/custom-login-redirect/'  # Redireciona após login
#ACCOUNT_SIGNUP_REDIRECT_URL = '/accounts/custom-login-redirect/'  # Redireciona após cadastro


DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100MB

