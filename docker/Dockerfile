FROM python:3.9

# Install system dependencies
RUN apt-get update && \
    apt-get install -y curl && \
    apt-get install -y poppler-utils  && \
    # apt-get install -y libglib2.0-0 libgl1-mesa-glx &&\
    rm -rf /var/lib/apt/lists/*

# Install Ollama using the provided install script.
RUN curl https://ollama.ai/install.sh | sh

# Expose necessary ports (Ollama's API port and Flask's port).
EXPOSE 11434 5000

# Set the working directory.
WORKDIR /app

# Copy the Python dependencies file from the docker folder.
COPY requirements.txt /app/

# Install Python dependencies.
RUN pip3 install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy entrypoint script from the docker folder.
ENV DISPLAY :99
COPY entrypoint.sh /usr/bin/entrypoint.sh
RUN chmod +x /usr/bin/entrypoint.sh
