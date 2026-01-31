#!/bin/bash

# Script para descargar el análisis histórico desde GitHub

OUTPUT_FILE="src/config/json/analisis_historico.json"
URL="https://raw.githubusercontent.com/Alfesito/ES-News-Topics/refs/heads/main/Objective%20View/analisis_historico.json"

echo "📥 Descargando análisis histórico desde GitHub..."

if curl -s -o "$OUTPUT_FILE" "$URL"; then
    echo "✅ Análisis descargado exitosamente en: $OUTPUT_FILE"
else
    echo "❌ Error al descargar el archivo"
    exit 1
fi
