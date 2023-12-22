# Use Python 3.11 slim as the base image
FROM python:3.11-slim-buster


# Allow statements and log messages to immediately appear in the knative logs
ENV PYTHONNUNBUFFERED True

# Set the working directory inside the container
ENV APP_HOME /app
WORKDIR $APP_HOME

# Copy only the requirements file initially to leverage Docker cache
COPY requirements.txt .

# Install project dependencies
RUN pip install -r requirements.txt

# Copy the rest of the project into the container
COPY . ./

# Expose the port your app runs on

# Command to run the application
CMD exec gunicorn --bind :$PORT --workers 3 --threads 8 --timeout 0 app:app
