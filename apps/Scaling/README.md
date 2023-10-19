# Scaler

## Scaling Schema
You can switch between different scaling methods by changing the Scaling Schema ENV VAR.

### Schema 1

### Schema 2

### ...

## Server Capacity 
Since we have a maximum of 6 servers to scale with, let's assume that we have a base server stack that can handle the minimum number of players a game has seen. This gives us the flexibility to assign fewer players per server, leading to much more active scaling.

This might be solved automatically.


## Start docker
```bash
docker run -d -p 5005:5005 \
-e OS_AUTH_URL=https://cloud.cs.oslomet.no:5000/v3 \
-e OS_PROJECT_NAME=ACIT4410_H23_s350233 \
-e OS_USERNAME=s350233 \
-e OS_PASSWORD="thumbnail personable lowercase" \
-e GAME_NAME ="NAME OF GAME TO SCAL FOR" \
-e SERVER_CAPACITY ="INT, SERVER CAPASITY" \
-e SCALING_SCHEME = INT \  # Number to pick the scaling schema
```