#!/bin/bash
# Start Ollama service in the background.
ollama serve &
# Wait a few seconds for the service to initialize.
sleep 5

# Check if model is already downloaded; if not, download it.
if ! ollama list | grep -q 'llama3.2-vision'; then
    echo "Model not found, downloading..."
    ollama run llama3.2-vision &
else
    echo "Model already downloaded."
fi

# Poll for model readiness
echo "Waiting for llama3.2-vision model to be ready..."
until ollama list | grep -q 'llama3.2-vision'; do
    echo "Model not ready, waiting..."
    sleep 2
done

echo "Model is ready."

# Set environment variables for Flask.
export FLASK_APP=app.py
export FLASK_DEBUG=1
export FLASK_RUN_PORT=5000
export FLASK_RUN_HOST=0.0.0.0

# Start the Flask application.
flask run
