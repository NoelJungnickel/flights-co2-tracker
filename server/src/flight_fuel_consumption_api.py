import requests
from typing import Optional, Dict


def get_flight_fuel_consumption(icao24_distance: Dict[str, float]) -> Optional[Dict]:
    """Retrieves the fuel consumption of flights.

    Args:
        icao24_distance (Dict[str, float]): Dictionary containing icao24 codes
            as key with their flight distance in nautical miles.
    """
    print({",".join(icao24_distance.keys())}, flush=True)
    print({",".join(str(val) for val in icao24_distance.values())}, flush=True)
    url = (
        f"https://despouy.ca/flight-fuel-api/q/?aircraft={','.join(icao24_distance.keys())}"
        f"&distance={','.join(str(val) for val in icao24_distance.values())}"
    )
    try:
        response = requests.get(url, timeout=(10))

        if response.ok:
            return response.json()
        else:
            return None
    except requests.exceptions.Timeout:
        print("The request timed out")
        return None
