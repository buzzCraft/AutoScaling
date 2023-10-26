import requests
from typing import List, Dict, Union, Optional
import time


# Base URL for Prometheus server
PROMETHEUS_URL = "http://10.196.37.200:9090"

def fetch_data_from_prometheus(endpoint: str, params: Dict[str, Union[str, int]]) -> List[Dict]:
    """Fetch data from Prometheus using given endpoint and parameters."""
    response = requests.get(f"{PROMETHEUS_URL}/{endpoint}", params=params)
    
    if response.status_code != 200:
        raise ValueError(f"Invalid response from server: {response.status_code} - {response.text}")
    
    return response.json()['data']['result']

def get_prometheus_historical_data(query: str, start: int, end: int, step: int) -> List[Dict]:
    """Fetch historical data from Prometheus."""
    params = {'query': query, 'start': start, 'end': end, 'step': step}
    return fetch_data_from_prometheus("api/v1/query_range", params)

def get_prometheus_latest_data(query: str) -> List[Dict]:
    """Fetch the latest data from Prometheus."""
    results = fetch_data_from_prometheus("api/v1/query", {'query': query})
    
    # Extract the latest value if available
    for item in results:
        if 'value' in item:
            item['values'] = [item['value']]
            del item['value']
    return results

def server_status(instance: str = "10.196.37.200:5000", 
                  start: Optional[int] = None, 
                  end: Optional[int] = None, 
                  step: Optional[int] = None, 
                  historical: bool = False) -> List[Dict]:
    """Return the status of a server."""
    query = f'running_servers_total{{instance="{instance}", job="openstack"}}'
    if historical:
        if not all([start, end, step]):
            raise ValueError("start, end, and step must be specified for historical data")
        return get_prometheus_historical_data(query, start, end, step)
    else:
        return get_prometheus_latest_data(query)
    
def game_status(game: str, 
                instance: str = "10.196.36.11:80", 
                start: Optional[int] = None, 
                end: Optional[int] = None, 
                step: Optional[int] = None, 
                historical: bool = False) -> List[Dict]:
    """Return the status of a game."""
    query = f'player_count{{title="{game}", instance="{instance}", job="games"}}'
    if historical:
        if not all([start, end, step]):
            raise ValueError("start, end, and step must be specified for historical data")
        return get_prometheus_historical_data(query, start, end, step)
    else:
        return get_prometheus_latest_data(query)
    
def game_player_stats(game: str, instance: str = "10.196.36.11:80") -> Dict[str, Union[str, int]]:
    """
    Get the max and min player counts for the specified game from Prometheus data.
    
    Args:
    game: Name of the game.
    instance: The instance to be queried.
    
    Returns:
    A dictionary containing the game's title, minimum, and maximum player count.
    """
    
    # Set the start time to a far past value (e.g., 10 years ago)
    start = int(time.time()) - (10 * 365 * 24 * 3600)  # 10 years * 365 days/year * 24 hours/day * 3600 seconds/hour
    
    # Calculate the range in seconds from the start date to now
    range_seconds = int(time.time()) - start
    
    # Convert the range to a more human-readable format for the Prometheus query
    if range_seconds < 60:
        duration = f"{range_seconds}s"
    elif range_seconds < 3600:
        duration = f"{range_seconds // 60}m"
    elif range_seconds < 86400:
        duration = f"{range_seconds // 3600}h"
    else:
        duration = f"{range_seconds // 86400}d"
    
    # Fetch all player counts over the specified range
    query = f'player_count{{title="{game}", instance="{instance}", job="games"}}[{duration}]'
    results = get_prometheus_latest_data(query)
    
    if not results or 'values' not in results[0]:
        return {
            'title': game,
            'min': None,
            'max': None
        }
    
    # Extract player counts from the results
    counts = [int(value[1]) for value in results[0]['values']]
    
    # Find the maximum player count
    max_count = max(counts)
    
    # Find the minimum player count where the count is greater than 0
    min_count = min([count for count in counts if count > 0], default=None)
    
    return {
        'title': game,
        'min': min_count,
        'max': max_count
    }

def get_min_max(game:str)->List[int]:
    # Clean the response and return min and max
    resp = game_player_stats(game=game)
    return resp['min'],resp['max']

def get_current_players(game:str)->int:
    # Clean the response and return min and max
    resp = game_status(game=game)
    players = resp[0]['values'][0][1]
    return players

def get_running_servers()->int:
    # Clean the response and return min and max
    resp = server_status()
    servers = resp[0]['values'][0][1]
    return servers





if __name__ == "__main__":
    print(get_current_players("Team Fortress 2"))
    x = game_player_stats(game="Team Fortress 2")
    print("Min:", x['min'], "Max:", x['max'])
    print(get_running_servers())