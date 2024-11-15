FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY certs/ ./certs/

# Create non-root user
RUN useradd -m -U -u 1000 webhook && \
    chown -R webhook:webhook /app

USER webhook

EXPOSE 8443

CMD ["python", "app.py"]
