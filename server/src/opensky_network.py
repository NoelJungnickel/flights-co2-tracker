import requests
from requests.auth import HTTPBasicAuth
from typing import Optional, Tuple, Dict, TypedDict


class FlightResponse(TypedDict):
    icao24: str
    firstSeen: int
    estDepartureAirport: Optional[str]
    lastSeen: int
    estArrivalAirport: Optional[str]
    callsign: str
    estDepartureAirportHorizDistance: Optional[int]
    estDepartureAirportVertDistance: Optional[int]
    estArrivalAirportHorizDistance: Optional[int]
    estArrivalAirportVertDistance: Optional[int]
    departureAirportCandidatesCount: int
    arrivalAirportCandidatesCount: int


def get_states(
    username: str, password: str, bounding_box: Tuple[float, float, float, float]
) -> Optional[Dict]:
    """Retrieves the states of aircraft within a specified bounding box.

    Args:
        username (str): The username for authentication.
        password (str): The password for authentication.
        bounding_box (tuple[float, float, float, float]): A tuple containing the
            coordinates of the bounding box in the format (lamin, lomin, lamax, lomax).

    Returns:
        dict: A dictionary containing the response JSON if successful, None
            otherwise.
    """
    url = (
        f"https://opensky-network.org/api/states/all?lamin={bounding_box[0]}"
        f"&lomin={bounding_box[1]}&lamax={bounding_box[2]}&lomax={bounding_box[3]}"
    )

    try:
        response = requests.get(
            url, auth=HTTPBasicAuth(username, password), timeout=(10)
        )

        if response.ok:
            return response.json()
        else:
            return None
    except requests.exceptions.Timeout:
        print("The request timed out")
        return None


# TODO: improve return type and add docstring
def get_flights_of_aircraft_max_24h(
    icao: str, start: int, end: int, username: str, password: str
) -> Optional[list[FlightResponse]]:
    """Retrieves the flights of aircraft within a specified time interval which can't be longer than 24h.

    Args:
        icao (str): Icao code of aircraft
        start (int): start of time interval in unix timestamp format
        end (int): end of time interval in unix timestamp format
        username (str): The username for authentication.
        password (str): The password for authentication.


    Returns:
        dict: A dictionary containing the response JSON if successful, None
            otherwise.
    """
    day_in_seconds = 86400
    if (end - start) > day_in_seconds:
        return None

    url = (
        f"https://opensky-network.org/api/flights/aircraft/?icao24={icao}"
        f"&begin={start}&end={end}"
    )

    try:
        response = requests.get(
            url, auth=HTTPBasicAuth(username, password), timeout=(10)
        )

        if response.ok:
            return response.json()
        else:
            return None
    except requests.exceptions.Timeout:
        print("The request timed out")
        return None
