from utils import get_min_max, get_running_servers, get_current_players
from scale import Scaler
import logging
import os
import time  # import the time module
import dotenv


dotenv.load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    filename='scaler.log',  # Set the minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger('scaler')

## INIT
# Set up variables
games = os.getenv("GAME_NAME")
nub_server = int(os.getenv("NUMBER_OF_SERVERS"))
scaling_scheme = int(os.getenv("SCALING_SCHEME"))

logger.info(f"Game: {games}")
logger.info(f"Number of servers avaible: {nub_server}")
logger.info(f"Scaling scheme: {scaling_scheme}")


def setup_g(game, nub_server, capacity_per_server, baseload, fake=False):
    """ Calculate the baseload for the game """
    p_min, p_max = get_min_max(game=game)
    p_min=int(p_min)
    p_max=int(p_max)

    # Round down to nearest 5000 for easier calculations
    p_min = p_min - (p_min % 5000)
    # Round up to nearest 1000 for easier calculations
    p_max = p_max + (1000 - (p_max % 1000))
    # Set baseload to p_min
    if baseload != 0:
        baseload = p_min
    # Calculate server capacity
    fluctuation = p_max - baseload
    # Lets leave 10% of capacity for growth
    if capacity_per_server != 0:
        capacity_per_server = int(fluctuation*1.1 / nub_server)

    scaling_solution = Scaler(game=game, 
                            scaling_scheme=scaling_scheme, 
                            baseload=baseload, 
                            capacity_per_server=capacity_per_server,
                            fake=fake)
    return scaling_solution

game_list = games.split(",")
logger.info(f"Game list: {game_list}")
scaler_list = []
for game in game_list:
    logger.info(f"Setting up scaler for {game}")
    scaler_list.append(setup_g(game, nub_server, 0 ,0, fake=True))
    
## MAIN LOOP
while True:  # This will keep running indefinitely  
    # Call the scaler function with the scaling scheme selected, baseload, and capacity per server
    for scaler in scaler_list:
        scaler.scale()
    time.sleep(240)  # Introduce a delay of 240 seconds (4 minutes) before the next iteration






