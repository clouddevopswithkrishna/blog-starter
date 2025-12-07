FROM python:3.11-alpine

# Install required packages
RUN apk add --no-cache \
    docker-cli \
    curl \
    jq

# Install Flask and requests
RUN pip install flask requests

# Create directory for scripts
WORKDIR /app

# Copy monitoring script and dashboard
COPY monitor_container.sh /app/monitor_container.sh
COPY dashboard.py /app/dashboard.py

# Make scripts executable
RUN chmod +x monitor_container.sh dashboard.py

# Create log directory
RUN mkdir -p /var/log

ENV PYTHONUNBUFFERED=1

EXPOSE 8001

# Default command - use explicit paths and keep container alive
CMD ["sh", "-c", "python3 dashboard.py & ./monitor_container.sh live"]
