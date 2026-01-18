# Use the official lightweight Python image
FROM python:3.12-slim

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies
RUN pip install flask requests google-cloud-firestore gunicorn signalwire==2.1.1

# Run the web service on container startup using gunicorn
# Cloud Run passes the port as an environment variable
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app