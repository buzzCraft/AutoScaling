from utils import get_min_max, get_running_servers, get_current_players
from scale import Scaler
import logging
import os
import time  # import the time module
import dotenv
import random 


dotenv.load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    filename="scaler.log",  # Set the minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("scaler")

## INIT
# Set up variables
games = os.getenv("GAME_NAME")
nub_server = os.getenv("NUMBER_OF_SERVERS")
scaling_scheme = os.getenv("SCALING_SCHEME")
fake_list = os.getenv("FAKE")


# Split the environment variable strings into lists
game_list = games.split(",")
nub_server_list = nub_server.split(",")
scaling_scheme_list = scaling_scheme.split(",")
fake_list = fake_list.split(",")

# Resetting the game_count for the new iteration

game_count = {}
for game in game_list:
    game_count[game] = game_count.get(game, 0) + 1
game_occurrence = {}
list_of_games = []
for idx, game in enumerate(game_list):
    # Count the game occurrence for suffixing
    game_occurrence[game] = game_occurrence.get(game, 0) + 1
    # Format the game name with occurrence number if more than one, or with "1" if it occurs only once
    if game_count[game] > 1:
        game_name = f"{game} {game_occurrence[game]}"
    elif game_count[game] == 1:  # Check if there's only one game of this type
        game_name = f"{game} 1"
    else:
        game_name = game

    list_of_games.append(
        [
            game_name.strip(),  # .strip() to remove leading/trailing whitespace
            int(nub_server_list[idx]),
            int(scaling_scheme_list[idx]),
            int(fake_list[idx]),
        ]
    )




logger.info(f"Game: {games}")
logger.info(f"Number of servers avaible: {nub_server}")
logger.info(f"Scaling scheme: {scaling_scheme}")


def setup_g(game, nub_server, capacity_per_server, baseload, number = 1, scaler=1, fake=False):
    """Calculate the baseload for the game"""
    p_min, p_max = get_min_max(game=game)
    p_min = int(p_min)
    p_max = int(p_max)

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
    if capacity_per_server == 0:
        capacity_per_server = int(fluctuation * 1.1 / nub_server)
    
    logger.info(f"Game: {game}, Baseload: {baseload}, Capacity per server: {capacity_per_server}, ServerNumber: {number}")
    logger.info(f"Number of servers avaible: {nub_server}, Fake: {fake}, Scaling scheme: {scaler}")

    scaling_solution = Scaler(
        game=game,
        scaling_scheme=scaler,
        baseload=baseload,
        capacity_per_server=capacity_per_server,
        server_suffix = number,
        number_of_servers = nub_server,
        fake=fake,
    )
    logger.info(
        f"Game: {game}, Baseload: {baseload}, Capacity per server: {capacity_per_server}"
    )
    return scaling_solution


scaler_list = []
for game in list_of_games:
    logger.info(f"Setting up scaler for {game}")
    game_name = game[0]
    # The game name should be GameName 1, GameName 2, etc. if there are multiple games of the same type
    # Strip the number from the name and add it to a number var
    try:
        game_number = game_name.split(" ")[1]
    except:
        logger.info(f"Game {game_name} has no number")
        game_number = random.randint(1, 100)
    # And remove the number from the name
    game_name = game_name.split(" ")[0]
    nub_server = int(game[1])
    scaling_scheme = int(game[2])
    fake = int(game[3])
    scaler_list.append(
        setup_g(
            game=game_name,
            number = game_number,
            nub_server=nub_server,
            scaler=scaling_scheme,
            capacity_per_server=0,
            baseload=1,
            fake=fake,
        )
    )

## MAIN LOOP
while True:  # This will keep running indefinitely
    # Call the scaler function with the scaling scheme selected, baseload, and capacity per server
    for scaler in scaler_list:
        scaler.scale()
    time.sleep(
        240
    )  # Introduce a delay of 240 seconds (4 minutes) before the next iteration
