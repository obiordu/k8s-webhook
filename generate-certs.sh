#!/bin/bash

# Create certs directory
mkdir -p certs

# Generate CA key and certificate
openssl genrsa -out certs/ca.key 2048
openssl req -new -x509 -days 365 -key certs/ca.key -subj "/CN=admission-webhook-ca" -out certs/ca.crt

# Generate webhook key and CSR
openssl genrsa -out certs/webhook-key.pem 2048
openssl req -new -key certs/webhook-key.pem -subj "/CN=admission-webhook.default.svc" -out certs/webhook.csr

# Create certificate config
cat > certs/webhook-ext.conf << EOF
subjectAltName = DNS:admission-webhook.default.svc,DNS:admission-webhook.default.svc.cluster.local
EOF

# Sign the webhook certificate
openssl x509 -req -days 365 \
    -in certs/webhook.csr \
    -CA certs/ca.crt \
    -CAkey certs/ca.key \
    -CAcreateserial \
    -out certs/webhook-cert.pem \
    -extfile certs/webhook-ext.conf
