import os
import json
import re

# Directorio donde se encuentran los archivos JSON
directorio = "./json"

# Función para normalizar texto y dividir en palabras
def normalizar(texto):
    """Convierte un texto en un conjunto de palabras únicas en minúsculas."""
    return set(re.findall(r'\b\w+\b', texto.lower()))

# Recolectar todos los datos JSON
archivos_json = [f for f in os.listdir(directorio) if f.endswith(".json")]
json_data_list = []

for archivo in archivos_json:
    ruta_completa = os.path.join(directorio, archivo)
    with open(ruta_completa, 'r', encoding='utf-8') as f:
        try:
            datos = json.load(f)
            if isinstance(datos, list):
                json_data_list.extend(datos)
            else:
                print(f"Advertencia: {archivo} no contiene una lista JSON válida.")
        except json.JSONDecodeError:
            print(f"Error al decodificar el archivo: {archivo}")

# Extraer tags únicos de los datos iniciales
tags_unicos = set()
for item in json_data_list:
    if isinstance(item, dict):
        tags_unicos.update(tag.lower() for tag in item.get('tags', []))

# Actualizar los elementos con tags basados en coincidencias en title y subtitles
for item in json_data_list:
    if isinstance(item, dict):
        palabras_subtitles = normalizar(item.get('subtitles', ""))
        palabras_title = normalizar(item.get('title', ""))

        # Comparar palabras combinadas con tags únicos
        palabras_combinadas = palabras_subtitles | palabras_title
        coincidencias = tags_unicos & palabras_combinadas

        # Si no hay coincidencias en `tags_unicos`, añade de las palabras combinadas
        if not coincidencias:
            coincidencias = palabras_combinadas

        # Añadir los tags encontrados, capitalizando y evitando duplicados
        item['tags'].extend(tag.capitalize() for tag in coincidencias if tag.capitalize() not in item['tags']) # mejorar y precisar

# Guardar el JSON consolidado en un archivo único
archivo_salida = os.path.join(directorio, "merged_json.json")
with open(archivo_salida, 'w', encoding='utf-8') as f:
    json.dump(json_data_list, f, indent=4, ensure_ascii=False)

print("Procesamiento completado. Archivo consolidado guardado en:", archivo_salida)