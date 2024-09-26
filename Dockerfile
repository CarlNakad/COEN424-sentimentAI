# Start with python 3.11 image
FROM python:3.11-slim

# Copy the current directory into /app on the image
WORKDIR /app

# Copy the requirements file used for dependencies
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the rest of the working directory contents into the container at /app
COPY . .

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Run app.py when the container launches
CMD ["uvicorn", "app.main.py:app", "--host", "0.0.0.0", "--port", "3000"]