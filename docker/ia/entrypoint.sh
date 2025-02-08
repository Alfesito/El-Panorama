#!/bin/sh
# Iniciar Ollama en segundo plano
ollama serve &

# Esperar unos segundos para que arranque
sleep 5

# Descargar o cargar el modelo de DeepSeek
ollama run deepseek || true

# Iniciar la API
uvicorn deepseek_api:app --host 0.0.0.0 --port 8000