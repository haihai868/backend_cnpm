# Use a minimal Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies efficiently
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]