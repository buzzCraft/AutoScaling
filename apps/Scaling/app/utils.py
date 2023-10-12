import requests

PROMETHEUS_URL = "http://10.196.37.200:9090"

def get_prometheus_historical_data(query, start, end, step):
    response = requests.get(f"{PROMETHEUS_URL}/api/v1/query_range", params={
        'query': query,
        'start': start,
        'end': end,
        'step': step
    })
    results = response.json()['data']['result']
    return results

def get_prometheus_latest_data(query):
    response = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={'query': query})
    results = response.json()['data']['result']
    # Extract the latest value if available
    for item in results:
        if 'value' in item:
            item['values'] = [item['value']]
            del item['value']
    
    return results

def server_status(start=None, end=None, step=None, hisorical=False):
    query = 'running_servers_total{instance="10.196.37.200:5000", job="openstack"}'
    if hisorical:
        if start is None or end is None or step is None:
            raise ValueError("start, end and step must be specified for historical data")
        return get_prometheus_historical_data(query, start, end, step)
    else:
        return get_prometheus_latest_data(query)
    

def game_status(game, start=None, end=None, step=None, hisorical=False):
    query = f'player_count{{title="{game}", instance="10.196.36.11:80", job="games"}}'
    if hisorical:
        if start is None or end is None or step is None:
            raise ValueError("start, end and step must be specified for historical data")
        return get_prometheus_historical_data(query, start, end, step)
    else:
        return get_prometheus_latest_data(query)

    


if __name__ == "__main__":
    import time
    end_time = int(time.time())
    start_time = end_time - (4 * 3600)  # 4 hours ago
    step = 5 * 60  # 5 minutes

    print(game_status("Team Fortress 2"))
    print(server_status())

