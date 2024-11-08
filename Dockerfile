FROM python:3.11.3
ENV PYTHONUNBUFFERED True

# Install dependencies
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set working directory
ENV APP_HOME /root
WORKDIR $APP_HOME

# Copy app directory to container
COPY ./app $APP_HOME/app

# Set the Python module search path
ENV PYTHONPATH=$APP_HOME/app

# Expose port 8080 for Google Cloud Run
EXPOSE 8080

# Start FastAPI app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]