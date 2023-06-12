import requests
from requests.auth import HTTPBasicAuth
from typing import Optional


def get_states(
    username: str, password: str, bounding_box: tuple[float, float, float, float]
) -> Optional[dict]:
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

        if response.ok:
            return response.json()
        else:
            return None
    except requests.exceptions.Timeout:
        print("The request timed out")
        return None
