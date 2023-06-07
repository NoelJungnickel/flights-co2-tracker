import requests
from requests.auth import HTTPBasicAuth

def get_states():
    response = requests.get('https://opensky-network.org/api/states/all?lamin=52.3418234221&lomin=13.0882097323&lamax=52.6697240587&lomax=13.7606105539',
                                                    auth = HTTPBasicAuth('swinarga', 'GgBUVknLM2@j4YE'))
    if (response.ok):
        return response.json()
    else:
        return None