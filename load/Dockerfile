FROM python:3.11-slim

# Install requests
RUN pip install requests

WORKDIR /app

COPY stress_app.py .

CMD ["python", "stress_app.py"]
