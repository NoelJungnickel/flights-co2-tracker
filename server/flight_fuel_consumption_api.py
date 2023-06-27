import requests
from typing import Optional, Tuple, Dict

# https://despouy.ca/flight-fuel-api/


def get_flight_fuel_consumption(
    icao24_distance_list: list[Tuple[str, float]]
) -> Optional[Dict]:
    """Retrieves the fuel consumption of flights.

    Args:
      icao24_distance_list (list): list of tuples containing an icao24 code
        and their flight distance in nautical miles. (icao24_code, distance)
    """
    icao24_list = map(lambda flight: flight[0], icao24_distance_list)
    distance_list = map(lambda flight: flight[1], icao24_distance_list)

    url = (
        f"https://despouy.ca/flight-fuel-api/q/?aircraft={','.join(icao24_list)}"
        f"&distance={','.join(str(x) for x in distance_list)}"
    )
    print(url)
    try:
        response = requests.get(url, timeout=(10))

        if response.ok:
            return response.json()
        else:
            print(response.text)
            return None
    except requests.exceptions.Timeout:
        print("The request timed out")
        return None
