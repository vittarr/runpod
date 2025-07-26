FROM python:3.10-slim

# Basic setup
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# Add code
COPY . /app
WORKDIR /app

# RunPod serverless handler
CMD ["python", "handler.py"]
