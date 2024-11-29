FROM python:3.11.3
ENV PYTHONUNBUFFERED True

# Install dependencies
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set working directory
WORKDIR /app

# Copy app directory to container
COPY ./app /app

# Set the Python module search path
ENV PYTHONPATH=/app

# Expose port 8080 for Google Cloud Run
EXPOSE 8080

# Start FastAPI app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]