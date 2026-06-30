FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Run the application with Gunicorn, binding to the port provided by the environment (Railway)
CMD gunicorn --bind 0.0.0.0:${PORT:-5000} app:app
