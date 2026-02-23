# Docker Deployment Guide for CAPP Application

## Prerequisites
- Docker Desktop installed ([Download](https://www.docker.com/products/docker-desktop))
- Docker Compose installed (included with Docker Desktop)

## Quick Start

### 1. Build and Run with Docker Compose (Recommended)

```bash
# Navigate to project directory
cd "C:\Users\Adm\Desktop\CAPP-AI project"

# Build and start all services
docker-compose up --build

# In another terminal, download a model (e.g., phi)
docker exec capp-ollama ollama pull phi
```

This will:
- Start the Ollama service on `localhost:11434`
- Start the CAPP application
- Create persistent volumes for data

### 2. Build Docker Image Only

```bash
docker build -t capp-app:latest .
```

### 3. Run Container

```bash
# Without Ollama (requires external Ollama service)
docker run -it --rm \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  capp-app:latest

# With docker-compose (recommended)
docker-compose up
```

## Useful Docker Commands

```bash
# View running containers
docker ps

# View logs
docker logs capp-app
docker logs capp-ollama

# Stop all services
docker-compose down

# Remove volumes (clears Ollama models)
docker-compose down -v

# Rebuild without cache
docker-compose up --build --no-cache

# Pull a model into Ollama
docker exec capp-ollama ollama pull llama2
docker exec capp-ollama ollama pull neural-chat
```

## Important Notes

### Current Limitations
- **Tkinter GUI**: Your current Tkinter GUI won't display in Docker. 
- **Solution**: For online deployment, you should convert to a web interface (Flask/FastAPI)

### To Use This Docker Setup

**Option 1: Desktop Use** (with display)
```bash
# On Windows with Docker Desktop
docker run -it --rm \
  -e DISPLAY=host.docker.internal:0 \
  capp-app:latest
```

**Option 2: Recommended - Web Deployment** 
Convert your app to Flask (see below)

## Converting to Web Application (For Online Deployment)

Create `app_web.py`:

```python
from flask import Flask, request, jsonify
from capp_turning_planner import generate_turning_plan
from chat_ollama import query_ollama

app = Flask(__name__)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    file = request.files['file']
    model = request.form.get('model', 'phi')
    
    result = generate_turning_plan(file.filename, with_ai=True)
    return jsonify(result)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    response = query_ollama(data['message'], model=data.get('model', 'phi'))
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

Update `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir flask flask-cors -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "app_web.py"]
```

## Deployment Targets

### Local Testing
```bash
docker-compose up
# Access at http://localhost:5000 (if using Flask)
```

### Cloud Platforms

**Docker Hub**
```bash
docker build -t yourusername/capp-app:1.0 .
docker push yourusername/capp-app:1.0
```

**AWS/Google Cloud/Azure**
- Push to container registry
- Deploy to Cloud Run, ECS, or AKS

**Heroku** (if using Flask)
```bash
heroku container:push web
heroku container:release web
```

## Environment Variables

Set these in `docker-compose.yml` or at runtime:

```bash
OLLAMA_HOST=http://ollama:11434
OLLAMA_TIMEOUT=180
OLLAMA_AI_TIMEOUT=120
```

## Troubleshooting

```bash
# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}"

# View detailed logs
docker logs -f capp-app

# Verify Ollama is running
docker exec capp-ollama curl http://localhost:11434/api/tags

# Access container shell
docker exec -it capp-app bash
```

## Next Steps
1. Test locally with `docker-compose up`
2. Consider converting to Flask for true online deployment
3. Push to cloud registry (Docker Hub, AWS ECR, etc.)
4. Deploy to cloud platform of choice
