import json
import os
import django

# 🔹 Configura o ambiente Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "apapesc.settings_local")  # ajuste se o nome do seu projeto for diferente
django.setup()

from django.contrib.auth.models import User

# 🔹 Carrega o arquivo JSON
with open("usuarios.json", "r", encoding="utf-8") as f:
    usuarios = json.load(f)

# 🔹 Contadores
criados = 0
ignorados = 0

for user_data in usuarios:
    email = user_data["email"]    
    username = user_data["username"]
    first_name = user_data["primeiro_nome"]
    last_name = user_data["sobrenome"]
    senha = user_data["senha"]

    # 🔒 Verifica se já existe um usuário com mesmo username ou email
    if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
        print(f"⚠️ Usuário já existe: {username} / {email}")
        ignorados += 1
        continue

    # 🔹 Criação segura de usuário
    user = User.objects.create_user(
        email=email,        
        username=username,
        first_name=first_name,
        last_name=last_name,
        password=senha
    )
    user.save()
    print(f"✅ Usuário criado: {username}")
    criados += 1

print("\n📊 Resumo:")
print(f"Usuários criados: {criados}")
print(f"Usuários ignorados (já existiam): {ignorados}")
