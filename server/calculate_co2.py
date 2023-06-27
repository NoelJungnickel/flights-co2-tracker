from geopy import distance as geopy_distance  # type: ignore
import math
from typing import Tuple
import queue
from flight_fuel_consumption_api import get_flight_fuel_consumption


class CarbonComputation:
    """Class to compute total carbon emission in given airspace.

    Args:
        airspace_name (str): Name of watched airspace (e.g Berlin).
        bounding_box (Tuple): Bounding box of the watched airspace.
            bounding box = (lamin, lomin, lamax, lomax)
                (lamin, lomin) -> south west
                (lamax, lomin) -> north west
                (lamax, lomax) -> north east
                (lamin, lomax) -> south east
    """

    def __init__(
        self, airspace_name: str, bounding_box: Tuple[float, float, float, float]
    ) -> None:
        self.airspace_name: str = airspace_name
        self.bounding_box: Tuple[float, float, float, float] = bounding_box
        self.aircrafts_in_airspace: dict[str, dict] = {}
        self.jobqueue: queue.Queue = queue.Queue()

    def worker_main(self) -> None:
        """Entry point for the worker thread of a given city."""
        while 1:
            try:
                job_func = self.jobqueue.get()
                job_func()
                self.jobqueue.task_done()
            except KeyboardInterrupt:
                print(f"{self.airspace_name} worker exiting...")
                break

    def get_co2_emission(
        self, states: list, request_time: int, exit_time_threshold: int = 75
    ) -> float:
        """Returns the CO2 emission of flights in the current request-response cycle.

            1. Keep track of the aircraft state from current and previous requests
                and store it in the aircrafts_in_airspace instance variable.
            2. If an aircrafts previous state is known, calculate the distance
                between the aircraft's previous position and the current position.
            3. Determine which aircrafts are no longer in the airspace. If said aircraft's
                latest position is on ground, then no further calculations are needed.
                Otherwise, calculate the distance from the latest recorded position to
                the edge of the bounding box.
            4. Create a list of (icao24, distance) Tuples and query the flight fuel
                consumption api with it.
            5. Create two lists from the API response:
                - List of CO2 emissions of aircrafts,
                    which have their fuel consumption rate known by the API.
                - List of icao24 codes of aircrafts,
                    which don't have their fuel consumption rate known by the API.
            6. Calculate the CO2 emission of aircrafts with unknown fuel consumption rate.
            7. Sum the CO2 emission of both lists.
            8. Remove aircrafts that are no longer in the airspace.
            9. Remove curr_distance attribute because it should not carry over
                to the next request-response cycle.

        Args:
            states (list): A list of aircraft states received from /states/all endpoint
                of the OpenSky Network API.
            request_time (int): The time that the request was sent in seconds since epoch.
            exit_time_threshold (int): The amount of time needed to determine that
                the  aircraft is no longer in the airspace. Defaults to 60 seconds.
        """
        self.update_aircrafts_in_airspace(states, request_time)

        # find out which aircrafts are no longer in the airspace
        aircraft_id_not_in_airspace = []
        for aircraft_id in self.aircrafts_in_airspace:
            aircraft = self.aircrafts_in_airspace[aircraft_id]

            # if the last position update was more than x seconds ago,
            # then assume its not in the airspace anymore
            if request_time - aircraft["last_update"] >= exit_time_threshold:
                aircraft_id_not_in_airspace.append(aircraft_id)

        # calculate the CO2 emission of aircrafts that are no longer in the airspace
        # as the state object of an aircraft may still appear in the next request cycle.
        for aircraft_id in aircraft_id_not_in_airspace:
            aircraft = self.aircrafts_in_airspace[aircraft_id]
            state = aircraft["curr_state"]

            if state["on_ground"]:
                continue

            edge_position = self.get_edge_position(
                state["true_track"],
                self.bounding_box,
                (state["longitude"], state["latitude"]),
            )
            # calculate the distance that the aircraft was in the airspace
            distance = geopy_distance.great_circle(
                (state["latitude"], state["longitude"]),
                (edge_position[0], edge_position[1]),
            ).km

            if distance > 0:
                self.aircrafts_in_airspace[aircraft_id]["curr_distance"] = distance

        print(f"aircrafts in airspace: {self.aircrafts_in_airspace}")

        # create icao24_distance_list
        icao24_distance_list = [
            (icao24, geopy_distance.Distance(kilometers=state["curr_distance"]).nautical)
            for icao24, state in self.aircrafts_in_airspace.items()
            if state.get("curr_distance")
        ]
        print(icao24_distance_list)

        new_co2_emission = 0
        if icao24_distance_list:
            # get co2 emission from flight fuel consumption api
            flight_fuel_list = get_flight_fuel_consumption(icao24_distance_list)

            if flight_fuel_list:
                # list of co2 emissions of aircrafts with known fuel consumption
                co2_list = [
                    flight["co2"] for flight in flight_fuel_list if flight.get("co2")
                ]

                # list of icao24 codes with unknown fuel consumption
                no_co2_icao24_list = [
                    flight["icao24"]
                    for flight in flight_fuel_list
                    if flight.get("co2") is None
                ]

                print(f"no_co2_icao24: {no_co2_icao24_list}")

                assumed_co2_list = [
                    self.calculate_co2_emission(state["curr_distance"])
                    for icao24, state in self.aircrafts_in_airspace.items()
                    if icao24 in no_co2_icao24_list
                    and state.get("curr_distance") is not None
                ]

                new_co2_emission += sum(co2_list) + sum(assumed_co2_list)
        print(f"aircrafts NOT in airspace: {aircraft_id_not_in_airspace}")

        # remove aircrafts no longer in airspace
        for aircraft_id in aircraft_id_not_in_airspace:
            del self.aircrafts_in_airspace[aircraft_id]

        # remove curr_distance for aircrafts in airspace
        for icao24, state in self.aircrafts_in_airspace.items():
            if state.get("curr_distance"):
                del state["curr_distance"]

        return new_co2_emission

    def update_aircrafts_in_airspace(self, states: list, request_time: int) -> None:
        """Updates the instance variable aircrafts_in_airspace.

        Args:
            states (list): A list of aircraft states received from /states/all endpoint
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

            curr_state = {
                "time_position": time_position,
                "longitude": longitude,
                "latitude": latitude,
                "on_ground": on_ground,
                "velocity": velocity,
                "true_track": true_track,
            }
            if self.aircrafts_in_airspace.get(state[0]) is not None:
                prev_state = self.aircrafts_in_airspace[state[0]]["curr_state"]
                prev_position = (prev_state["latitude"], prev_state["longitude"])
                curr_position = (curr_state["latitude"], curr_state["longitude"])

                # calculate distance between previous and current position
                distance = geopy_distance.great_circle(prev_position, curr_position).km
                if distance > 0:
                    self.aircrafts_in_airspace[state[0]]["curr_distance"] = distance

                # if distance > 0:
                #     icao24_distance_list.append({
                #         "icao24": state[0],
                #         "distance": distance
                #     })

                self.aircrafts_in_airspace[state[0]]["last_update"] = request_time
                self.aircrafts_in_airspace[state[0]]["curr_state"] = curr_state
            else:
                self.aircrafts_in_airspace[state[0]] = {
                    "last_update": request_time,
                    "curr_state": curr_state,
                }

    def get_edge_position(
        self,
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
        self, distance: float, fuel_consumption_rate: float = 3.0
    ) -> float:
        """Calculates the amount of CO2 emission of a flight.

        Args:
            distance (float): The distance of the (partial-)flight in km.
            fuel_consumption_rate (float, optional): The rate of fuel consumption
                of an aircraft in kilograms per kilometers. Defaults to 3.0 kg/km

        Returns:
            float: The amount of CO2 emission in kilograms.
        """
        fuel_used_kg = fuel_consumption_rate * distance
        co2_kg = fuel_used_kg * 3.15
        return co2_kg
