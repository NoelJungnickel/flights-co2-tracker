import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from typing import Optional, Tuple, Dict, List, Any, Union


def _transform_state_vector(states: List[List[Any]]) -> Dict[str, Dict[str, Any]]:
    """Transforms states into dictionary containing the useful information.

    Args:
        states (List[Dict[str, Any]]): An airstate vector in the opensky format to
            be converted.

    Returns:
        Dict[str, Any]: Dictionary representing the airspace. Keys are ids of
            aircrafts and values are dictionaries with data containing position,
            velocity and true_track.
    """
    current_aircrafts = {}
    for state in states:
        if state[5] and state[6] and state[9] and state[10]:
            current_aircrafts[state[0]] = {
                "last_update": state[4],
                "position": (state[6], state[5]),
                "on_ground": state[8],
                "velocity": state[9],
                "true_track": state[10],
            }
    return current_aircrafts


def get_states_of_bounding_box(
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
        response = requests.get(url, auth=HTTPBasicAuth(username, password), timeout=(10))

        if response.ok and response.json() and response.json().get("states"):
            response_json = response.json()
            response_json["states"] = _transform_state_vector(response_json["states"])
            return response_json
        else:
            return None
    except requests.exceptions.Timeout:
        print("The states-request timed out")
        return None


def get_flights_by_aircrafts(
    icao24: str, start: datetime, end: datetime
) -> List[Dict[str, Union[str, int]]]:
    """Retrieves flight data of given aircraft in specified time.

    Args:
        icao24 (str): Icao24 code of the aircraft.
        start (datetime): Start time of the request.
        end (datetime): End time of the request.
    """
    start_time = int(start.timestamp())
    end_time = int(end.timestamp())

    # Check, if given time is within the Opensky limit of 30 days
    if end_time <= start_time or end_time - start_time > 3600 * 24 * 30:
        return []
    url = (
        f"https://opensky-network.org/api/flights/aircraft/?icao24={icao24}"
        f"&begin={start_time}&end={end_time}"
    )

    try:
        response = requests.get(url, timeout=(10))

        if response.ok:
            return response.json()
        else:
            return []
    except requests.exceptions.Timeout:
        print("The flights-request timed out")
        return []
