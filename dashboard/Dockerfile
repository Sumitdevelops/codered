FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py .

EXPOSE 8501 8502

# Default to demo UI, can be overridden in docker-compose
CMD ["streamlit", "run", "demo_ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
