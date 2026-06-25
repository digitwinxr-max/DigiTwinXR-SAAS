FROM python:3.11-slim

WORKDIR /app

# Copy entire GCDTP project structure
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set PYTHONPATH to include parent directory for "backend.src" imports
ENV PYTHONPATH=/app

COPY . .

EXPOSE 8080

CMD ["uvicorn", "backend.src.main:app", "--host", "0.0.0.0", "--port", "8080"]
