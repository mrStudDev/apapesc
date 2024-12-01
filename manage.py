#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Função principal para inicializar o Django."""
    # Define o ambiente padrão, caso `ENV_TYPE` não esteja configurado
    env_type = os.getenv("ENV_TYPE", "local")

    # Configura o módulo de settings com base no tipo de ambiente
    if env_type == "local":
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings_local")
    elif env_type == "production":
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings_production")
    else:
        raise ValueError(f"Ambiente desconhecido: {env_type}")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Não foi possível importar Django. Certifique-se de que está instalado "
            "e disponível no ambiente virtual."
        ) from exc

    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()

