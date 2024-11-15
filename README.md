# Kubernetes Admission Webhook

A simple and efficient Kubernetes admission webhook that provides both validation and mutation capabilities for your cluster.

## Features

### Validation
- Enforces required labels (e.g., 'app' label)
- Prevents privileged container execution
- Ensures containers run as non-root users

### Mutation
- Adds default labels (e.g., 'environment: production')
- Sets default resource limits and requests for containers

## Prerequisites

- Python 3.11+
- Docker
- Kubernetes cluster with admission webhook support
- OpenSSL for generating certificates

## Quick Start

1. Generate certificates:
```bash
./generate-certs.sh
```

2. Build and run locally:
```bash
pip install -r requirements.txt
python app.py
```

3. Build and run with Docker:
```bash
docker build -t k8s-webhook:latest .
docker run -p 8443:8443 -v $(pwd)/certs:/app/certs k8s-webhook:latest
```

4. Deploy to Kubernetes:
```bash
kubectl apply -f k8s/
```

## Configuration

The webhook supports the following environment variables:
- `PORT` (default: 8443)
- `HOST` (default: 0.0.0.0)
- `LOG_LEVEL` (default: INFO)

## Testing

Test the webhook endpoints:

```bash
# Test validation
curl -k -X POST https://localhost:8443/validate -H "Content-Type: application/json" -d @test/validate-pod.json

# Test mutation
curl -k -X POST https://localhost:8443/mutate -H "Content-Type: application/json" -d @test/mutate-pod.json
```

## Security

- TLS encryption required
- Non-root container execution
- Minimal base image
- Least privilege principle
