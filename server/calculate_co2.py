from opensky_network import get_states
from geopy import distance as geopy_distance  # type: ignore
import time
import math
import schedule
import threading
from typing import Callable, Tuple
from redis import Redis
from argparse import ArgumentParser

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
aircrafts_in_airspace: dict[str, dict] = {}
total_co2_emission = {"value": 0.0}
redis = Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)


# bounding box = (lamin, lomin, lamax, lomax)
# (lamin, lomin) -> south west
# (lamax, lomin) -> north west
# (lamax, lomax) -> north east
# (lamin, lomax) -> south east

berlin_bounding_box = (52.3418234221, 13.0882097323, 52.6697240587, 13.7606105539)


def main() -> None:
    """Entry point of the application."""
    # Connecting to Redis Database
    parser = ArgumentParser()
    parser.add_argument("--username", type=str, help="Username for OpenSky")
    parser.add_argument("--password", type=str, help="Password for OpenSky")
    args = parser.parse_args()

    # Access username and password from console
    username = args.username
    password = args.password

    try:
        redis.info()
    except Exception:
        raise RuntimeError("Failed to connect to Redis.")

    byte_total_co2_emission = redis.hget("total", "berlin")
    if byte_total_co2_emission is not None:
        total_co2_emission["value"] = float(byte_total_co2_emission.decode())

    schedule.every(1).minutes.do(
        run_threaded,
        update_total_co2_emission_job,
        args=(username, password, berlin_bounding_box),
    )
    # start the first job now instead of waiting 1 minute
    schedule.run_all()

    # call opensky api every (1 + calculation time) minute(s)
    while True:
        schedule.run_pending()
        time.sleep(1)


def run_threaded(job_func: Callable, args: Tuple) -> None:
    """Runs a function in a separate thread.

    Args:
        job_func (Callable): The function to be executed in a separate thread
        args (tuple): The arguments to be passed to the function when it is called.

    """
    job_thread = threading.Thread(target=job_func, args=args)
    job_thread.start()


def update_total_co2_emission_job(
    username: str, password: str, bounding_box: Tuple[float, float, float, float]
) -> None:
    """Wrapper function for updating the total co2 emission.

    Should be executed as a job by the schedule library

    Args:
        username (str): The username for authentication.
        password (str): The password for authentication.
        bounding_box (tuple[float, float, float, float]): A tuple containing the
            coordinates of the bounding box in the format (lamin, lomin, lamax, lomax).

    """
    response = get_states(username, password, bounding_box)

    # response["states"] can be null
    if response is not None and response["states"] is not None:
        update_total_co2_emission(response["states"], response["time"])


def update_total_co2_emission(
    states: list, request_time: int, exit_time_threshold: int = 60
) -> None:
    """Updates the global variable total_co2_emission and stores it in Redis.

        1. Keeps track of the aircraft state from current and previous requests
            and store it in the aircrafts_in_airspace global variable.
        2. Determines which aircrafts are no longer in the airspace.
        3. Calculates the duration of those aircrafts in the airspace.
        4. Calculates the CO2 emission of those aircrafts based on their
            duration in the airspace.
        5. Sums the CO2 emission of each aircraft.
        6. Add the sum of the CO2 emission of each aircraft to the total_co2_emission
            global variable.
        7. Store the value of total_co2_emission in Redis.
        8. Remove aircrafts that are no longer in the airspace.

    Args:
        states (list): A list of aircraft states received from the /states/all endpoint
            of the OpenSky Network API.
        request_time (int): The time that the request was sent in seconds since epoch.
        exit_time_threshold (int): The amount of time needed to determine that
            the  aircraft is no longer in the airspace. Defaults to 60 seconds.
    """
    update_aircrafts_in_airspace(states, request_time)

    # find out which aircrafts are no longer in the airspace
    aircraft_id_not_in_airspace = []
    for aircraft_id in aircrafts_in_airspace:
        aircraft = aircrafts_in_airspace[aircraft_id]

        # if the last position update was more than x seconds ago,
        # then assume its not in the airspace anymore
        if request_time - aircraft["last_update"] >= exit_time_threshold:
            aircraft_id_not_in_airspace.append(aircraft_id)

    print(f"aircrafts in airspace: {aircrafts_in_airspace}")
    # calculate the CO2 emission of aircrafts that are no longer in the airspace
    # as the state object of an aircraft may still appear in the next request cycle.
    co2_emission_per_aircraft = []
    for aircraft_id in aircraft_id_not_in_airspace:
        # calculate the duration that the aircraft was in the airspace
        positions = aircrafts_in_airspace[aircraft_id]["positions"]
        durations = []

        for index, position in enumerate(positions):
            if index == len(positions) - 1:
                if position["on_ground"]:
                    continue
                # calculate duration to the edge of the bounding box
                # the edge is dictated by the plane's true_track

                # Get the position, where the aircraft would intersect
                # with the edge of the bounding box, if it were to keep
                # heading in the same direction until it reaches the edge
                # of the bounding box
                edge_position = get_edge_position(
                    position["true_track"],
                    berlin_bounding_box,
                    (position["longitude"], position["latitude"]),
                )

                # get the duration it would take to get to the edge position
                duration = calculate_duration(
                    (position["latitude"], position["longitude"]),
                    (edge_position[0], edge_position[1]),
                    position["velocity"],
                )
                durations.append(duration)
                continue

            next_position = positions[index + 1]

            duration = calculate_duration(
                (position["latitude"], position["longitude"]),
                (next_position["latitude"], next_position["longitude"]),
                position["velocity"],
            )
            durations.append(duration)
        print(f"aircraft_id: {aircraft_id}, durations: {durations}")
        total_duration = sum(durations)

        # calculate the CO2 emission
        co2_emission = calculate_co2_emission(total_duration)
        co2_emission_per_aircraft.append(co2_emission)

    total_co2_emission["value"] += sum(co2_emission_per_aircraft)
    redis.hset("total", "berlin", total_co2_emission["value"])
    print(f'total CO2: {total_co2_emission["value"]}')

    # remove aircrafts no longer in airspace
    for aircraft_id in aircraft_id_not_in_airspace:
        del aircrafts_in_airspace[aircraft_id]
    print("------------------------------")


def update_aircrafts_in_airspace(states: list, request_time: int) -> None:
    """Updates the global variable aircrafts_in_airspace.

    Args:
        states (list): A list of aircraft states received from the /states/all endpoint
            of the OpenSky Network API.
        request_time (int): The time that the request was sent in seconds since epoch
    """
    for state in states:
        time_position = state[3]
        longitude = state[5]
        latitude = state[6]
        on_ground = state[8]
        velocity = state[9]
        true_track = state[10]

        # longitude, latitude, velocity, true_track can be null
        if (
            longitude is None
            or latitude is None
            or velocity is None
            or true_track is None
        ):
            continue

        position = {
            "time_position": time_position,
            "longitude": longitude,
            "latitude": latitude,
            "on_ground": on_ground,
            "velocity": velocity,
            "true_track": true_track,
        }
        if aircrafts_in_airspace.get(state[0]) is not None:
            aircrafts_in_airspace[state[0]]["last_update"] = request_time
            aircrafts_in_airspace[state[0]]["positions"].append(position)
        else:
            aircrafts_in_airspace[state[0]] = {
                "last_update": request_time,
                "positions": [position],
            }


def calculate_duration(
    point1: Tuple[float, float], point2: Tuple[float, float], velocity: float
) -> float:
    """Calculates the duration of travel from one point to another with constant velocity.

    Args:
        point1 (tuple[float,float]): The first geographical point in degrees and
            in the format (latitude, longitude).
        point2 (tuple[float, float]): The second geographical point in degrees and
            in the format (latitude, longitude).
        velocity (float): The speed of the aircraft in meters per second.

    Returns:
        float: The duration in seconds to travel from point1 to point2 with
            constant velocity.
    """
    if velocity == 0:
        return 0.0

    # Get the distance between the two points in kilometers
    distance = geopy_distance.great_circle(point1, point2).km
    # Calculate the time required to travel the distance at the given velocity.
    time = (distance * 1000) / velocity
    return time


def get_edge_position(
    true_track: float,
    bounding_box: Tuple[float, float, float, float],
    position: Tuple[float, float],
) -> Tuple[float, float]:
    """Calculates the distance to the bounding box edge.

    Args:
        true_track (float): The direction of the aircraft in decimal degrees,
            measured clockwise from north (north = 0).
        bounding_box (tuple[float, float, float, float]): A tuple containing
            the coordinates of the bounding box in the format
            [lamin, lomin, lamax, lomax].
        position (tuple[float, float]): The geographical point of the aircraft
            in degrees and in the format (longitude, latitude).

    Returns:
        tuple[float, float]: The geographical coordinates (latitude, longitude)
            representing the edge position towards which the aircraft is heading.
    """
    lamin = bounding_box[0]
    lomin = bounding_box[1]
    lamax = bounding_box[2]
    lomax = bounding_box[3]

    pos_la = position[1]
    pos_lo = position[0]

    true_track %= 360

    # Quadrant I - true_track 0 deg - 90 deg
    # can be top or right edge
    if true_track >= 0 and true_track <= 90:
        sa = lamax - pos_la
        de = math.tan(math.radians(true_track)) * sa

        if pos_lo + de >= lomax:
            # meets right edge
            edge_pos_la = pos_la + (
                math.tan(math.radians(90 - true_track)) * (lomax - pos_lo)
            )
            edge_pos_lo = lomax
        else:
            # meets top edge
            edge_pos_la = lamax
            edge_pos_lo = pos_lo + de

        return (edge_pos_la, edge_pos_lo)

    # Quadrant II - true_track 90 deg - 180 deg
    # can be right or bottom edge
    if true_track >= 90 and true_track <= 180:
        sa = lomax - pos_lo
        de = math.tan(math.radians(true_track - 90)) * sa

        if pos_la - de <= lamin:
            # meets bottom edge
            edge_pos_la = lamin
            edge_pos_lo = pos_lo + (
                math.tan(math.radians(180 - true_track)) * (pos_la - lamin)
            )
        else:
            # meets right edge
            edge_pos_la = pos_la - de
            edge_pos_lo = lamax

        return (edge_pos_la, edge_pos_lo)

    # Quadrant III
    # can be left or bottom edge
    if true_track >= 180 and true_track <= 270:
        sa = pos_lo - lomin
        de = math.tan(math.radians(270 - true_track)) * sa

        if pos_la - de <= lamin:
            # meets bottom edge
            edge_pos_la = lamin
            edge_pos_lo = pos_lo - (
                math.tan(math.radians(90 - (270 - true_track))) * (pos_la - lamin)
            )
        else:
            # meets left edge
            edge_pos_la = pos_la - de
            edge_pos_lo = lomin

        return (edge_pos_la, edge_pos_lo)

    # Quadrant IV - true_track 270 deg - 360 deg
    # can be left or top edge
    if true_track >= 270 and true_track <= 360:
        sa = lamax - pos_la
        de = math.tan(math.radians(360 - true_track)) * sa

        if pos_lo - de <= lomin:
            # meets left edge
            edge_pos_la = pos_la + (
                math.tan(math.radians(90 - (360 - true_track))) * (pos_lo - lomin)
            )
            edge_pos_lo = lomin
        else:
            # meets top edge
            edge_pos_la = lamax
            edge_pos_lo = pos_lo - de

        return (edge_pos_la, edge_pos_lo)

    assert False, "Unreachable code - No quadrant matches"


def calculate_co2_emission(
    duration: float, fuel_consumption_rate: float = 378.54
) -> float:
    """Calculates the amount of CO2 emission of a flight.

    Args:
        duration (float): The duration of the flight in seconds.
        fuel_consumption_rate (float, optional): The rate of fuel consumption
            of an aircraft in kilograms per hour. Defaults to 378.54 kg/hour.

    Returns:
        float: The amount of CO2 emission in kilograms.
    """
    fuel_used_kg = fuel_consumption_rate * (duration / 3600)
    co2_kg = fuel_used_kg * 3.15
    return co2_kg


if __name__ == "__main__":
    main()
