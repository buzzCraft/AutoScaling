# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /OpenStack

# Copy the Python script into the container
COPY main.py .

# Install the OpenStack command-line client
RUN pip install --no-cache-dir python-openstackclient

# Command to run the script when the container starts
CMD ["python", "./main.py"]