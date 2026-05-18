import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

print("⏳ Convirtiendo archivos de Excel a formato binario ultra-ligero...")

# Leemos tus archivos Excel originales (que ya sabemos que están perfectos)
df_mortalidad = pd.read_excel(os.path.join(DATA_DIR, "NoFetal2019.xlsx"), engine="openpyxl")
df_cie10 = pd.read_excel(os.path.join(DATA_DIR, "CodigosDeMuerte.xlsx"), engine="openpyxl")
df_divipola = pd.read_excel(os.path.join(DATA_DIR, "Divipola.xlsx"), engine="openpyxl")

# Los guardamos como .feather dentro de la misma carpeta data
df_mortalidad.to_feather(os.path.join(DATA_DIR, "NoFetal2019.feather"))
df_cie10.to_feather(os.path.join(DATA_DIR, "CodigosDeMuerte.feather"))
df_divipola.to_feather(os.path.join(DATA_DIR, "Divipola.feather"))

print("✅ ¡Conversión exitosa! Ahora tienes archivos .feather super ligeros en tu carpeta 'data'.")