#!/bin/sh
set -e

echo "--- Ollama Entrypoint Starting ---"

ollama serve &
serve_pid=$!

sleep 3

echo "Waiting for Ollama server to be ready..."
until ollama ps >/dev/null 2>&1; do
  echo "Still waiting..."
  sleep 2
done

echo "Ollama server is up."

# Create model if missing
if ollama show gemma3:1b >/dev/null 2>&1; then
    echo "Model gemma3:1b already exists."
else
    echo "Model missing. Creating..."
    ollama create gemma3:1b -f /Modelfile
fi

echo "Model ready. Continuing."

wait $serve_pid
