# Use a Python 3.9 slim image as the base
FROM python:3.9-slim

# Install required packages including FastAPI and Uvicorn
RUN pip install fastapi uvicorn openstacksdk

# Copy scripts into the container
COPY /app/ /app/

# Set the working directory
WORKDIR /app

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]