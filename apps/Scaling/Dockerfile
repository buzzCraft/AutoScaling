FROM python:3.8-slim

# Install required packages
RUN pip install openstacksdk python-dotenv


# Copy scripts into the container
COPY /app/ /app/

# Set working directory
WORKDIR /app

# Expose the port the app runs on
EXPOSE 7474

# Command to run the application
CMD ["python", "app.py"]
