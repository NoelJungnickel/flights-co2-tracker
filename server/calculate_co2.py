from opensky_network import get_states
from geopy import distance as geopy_distance
import time
import math
from redis import Redis
from argparse import ArgumentParser

API_HOST = "127.0.0.1"
API_PORT = 8000
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
aircrafts_in_airspace = {}
total_co2_emission = 0
redis = Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)


# bounding box = (lamin, lomin, lamax, lomax)
# (lamin, lomin) -> south west
# (lamax, lomin) -> north west
# (lamax, lomax) -> north east
# (lamin, lomax) -> south east

berlin_bounding_box = (52.3418234221, 13.0882097323, 52.6697240587, 13.7606105539)


def main():
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

    if redis.hget("total", "berlin"):
        global total_co2_emission
        total_co2_emission = float(redis.hget("total", "berlin").decode())

    # call opensky api every (1 + calculation time) minute(s)
    while True:
        response = get_states(username, password, berlin_bounding_box)

        # response["states"] can be null
        if response is not None and response["states"] is not None:
            update_aircrafts_in_airspace(response["states"], response["time"])

        time.sleep(60)


def update_aircrafts_in_airspace(states, request_time):
    global total_co2_emission
    print(total_co2_emission)
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

    # find out which aircrafts are no longer in the airspace
    aircraft_id_not_in_airspace = []
    for aircraft_id in aircrafts_in_airspace:
        aircraft = aircrafts_in_airspace[aircraft_id]

        # last update was x seconds ago, then assume its not in the
        # airspace anymore
        if request_time - aircraft["last_update"] >= 60:
            aircraft_id_not_in_airspace.append(aircraft_id)

    co2_emission_per_aircraft = []
    for aircraft_id in aircraft_id_not_in_airspace:
        # calculate the duration that it was in the airspace
        positions = aircrafts_in_airspace[aircraft_id]["positions"]
        durations = []

        for index, position in enumerate(positions):
            if index == len(positions) - 1:
                if position["on_ground"]:
                    continue
                # calculate duration to the edge of the bounding box
                # the edge is dictated by the plane's true_track
                # north: 0,
                # east: 90,
                # south: 180,
                # west: 270

                # first get the position, where the aircraft would intersect with edge of the bounding box
                # if it were to keep heading at the same direction until it reaches the edge of the bounding box
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

            # assume velocity is constant from point a to point b
            duration = calculate_duration(
                (position["latitude"], position["longitude"]),
                (next_position["latitude"], next_position["longitude"]),
                position["velocity"],
            )
            durations.append(duration)
        total_duration = sum(durations)

        # calculate the co2 emission
        co2_emission = calculate_co2_emission(total_duration)
        co2_emission_per_aircraft.append(co2_emission)

    total_co2_emission += sum(co2_emission_per_aircraft)
    redis.hset("total", "berlin", total_co2_emission)

    # remove aircrafts no longer in airspace
    for aircraft_id in aircraft_id_not_in_airspace:
        del aircrafts_in_airspace[aircraft_id]


# point tuple should be (latitude, longitude)
# velocity in m/s
def calculate_duration(
    point1: tuple[float, float], point2: tuple[float, float], velocity: float
):
    if velocity == 0:
        return 0

    # get distance between the two points in km
    distance = geopy_distance.great_circle(point1, point2).km
    time = (distance * 1000) / velocity
    return time


# true_track in decimal degrees clockwise from north (north = 0)
# bounding_box is (lamin, lomin, lamax, lomax)
# position is (longitude, latitude)
def get_edge_position(
    true_track: float,
    bounding_box: tuple[float, float, float, float],
    position: tuple[float, float],
):
    lamin = bounding_box[0]
    lomin = bounding_box[1]
    lamax = bounding_box[2]
    lomax = bounding_box[3]

    pos_la = position[1]
    pos_lo = position[0]

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


# duration in seconds
# fuel_consumption_rate in kg per hour
def calculate_co2_emission(duration, fuel_consumption_rate=378.54):
    fuel_used_kg = fuel_consumption_rate * (duration / 3600)
    co2_kg = fuel_used_kg * 3.15
    return co2_kg


main()
