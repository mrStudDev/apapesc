import pandas as pd
import json

# 🔹 Carregar o arquivo Excel (ajuste conforme necessário)
arquivo_excel = "usuarios.xlsx"

# 🔹 Carregar os dados no DataFrame, garantindo que tudo seja string
df = pd.read_excel(arquivo_excel, dtype=str)

# 🔹 Renomear colunas corretamente conforme o Excel
df.columns = ["email", "username", "primeiro_nome", "sobrenome", "senha"]

# 🔹 Transformar em JSON
json_data = df.to_dict(orient="records")

# 🔹 Salvar o JSON no mesmo diretório
json_file = "usuarios.json"
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(json_data, f, indent=4, ensure_ascii=False)

print(f"✅ Arquivo JSON gerado com sucesso! Salvo como: {json_file}")
