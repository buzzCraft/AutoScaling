#!/bin/bash

# Define the image name
IMAGE_NAME="openstack-prometheus"

# Stop the container if it's running
CONTAINER_ID=$(docker ps -qf "ancestor=$IMAGE_NAME")
if [ ! -z "$CONTAINER_ID" ]; then
    echo "Stopping container $CONTAINER_ID..."
    docker stop $CONTAINER_ID
fi

# Remove the container
if [ ! -z "$CONTAINER_ID" ]; then
    echo "Removing container $CONTAINER_ID..."
    docker rm $CONTAINER_ID
fi

# Rebuild the Docker image
echo "Rebuilding $IMAGE_NAME..."
docker build -t $IMAGE_NAME .

# Run the container again
echo "Starting new container..."
docker run -d -p 5000:5000 \
-e OS_AUTH_URL=https://cloud.cs.oslomet.no:5000/v3 \
-e OS_PROJECT_NAME=ACIT4410_H23_s350233 \
-e OS_USERNAME=s350233 \
-e OS_PASSWORD="thumbnail personable lowercase" \
$IMAGE_NAME

echo "Done!"


