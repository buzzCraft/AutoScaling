FROM python:3.8-slim

# Install required packages
RUN pip install Flask openstacksdk

# Copy scripts into the container
COPY /app/ /app/

# Set working directory
WORKDIR /app

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]
