from utils import get_min_max, get_running_servers, get_current_players
from scaler import scale 
import logging
import os
import time  # import the time module

logging.basicConfig(
    level=logging.WARNING,
    filename='scaler.log',  # Set the minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger('scaler')

## INIT
# Set up variables
game = os.getenv("GAME_NAME"),
nub_server = int(os.getenv("NUMBER_OF_SERVERS")),
scaling_scheme = int(os.getenv("SCALING_SCHEME")),

# Get the current game status
p_min, p_max = get_min_max(game=game)
# Round down to nearest 1000 for easier calculations
p_min = p_min - (p_min % 1000)
# Round up to nearest 1000 for easier calculations
p_max = p_max + (1000 - (p_max % 1000))
# Set baseload to p_min
baseload = p_min
# Calculate server capacity
fluctuation = p_max - p_min
# Lets leave 10% of capacity for growth
capacity_per_server = fluctuation*1.1 / nub_server

## MAIN LOOP
while True:  # This will keep running indefinitely
    # Get the current game status
    current_players = get_current_players(game=game)
    # Get the current server status
    current_servers = get_running_servers()
    
    # Call the scaler function with the scaling scheme selected, baseload, and capacity per server
    scale(scaling_scheme, baseload, capacity_per_server)
    time.sleep(240)  # Introduce a delay of 240 seconds (4 minutes) before the next iteration






