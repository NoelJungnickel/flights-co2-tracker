import math
from typing import Tuple, Dict, Any, List
from geopy import distance as geopy_distance  # type: ignore
from flight_fuel_consumption_api import get_flight_fuel_consumption


class CarbonComputation:
    """Class to compute total carbon emission in given airspace.

    Args:
        airspace_name (str): Name of watched airspace (e.g Berlin).
        bounding_box (Tuple): Bounding box of the watched airspace.
            bounding box = (lamin, lomin, lamax, lomax)
                lamin = south border, lamax = north border
                lomin = west border, lomax = east border
    """

    def __init__(
        self, airspace_name: str, bounding_box: Tuple[float, float, float, float]
    ) -> None:
        self.airspace_name: str = airspace_name
        self.bounding_box: Tuple[float, float, float, float] = bounding_box
        self.aircrafts_in_airspace: Dict = {}
        self.bounding_box_diagonal: float = geopy_distance.distance(
            (bounding_box[0], bounding_box[1]), (bounding_box[2], bounding_box[3])
        ).km

    def get_co2_emission(
        self, states: List[List[Any]], request_time: int, exit_time_threshold: int = 300
    ) -> float:
        """Returns new carbon emission given new airspace state information.

            1. Bring the states vector to a better representation containing the useful
                information for each aircraft in a dictionary
            2. Keep track of the aircraft state from current and previous requests
                and store it in the aircrafts_in_airspace instance variable.
            3. Calculate the distance between the aircraft's previous position and
                its current position, if its previous state is known.
            4. Determine which aircrafts are no longer in the airspace. If said aircraft's
                latest position is on ground, then no further calculations are needed.
                Otherwise, calculate the distance from the latest recorded position to
                the edge of the bounding box.
            5. Create a list of (icao24, distance) tuples and query the flight fuel
                consumption API with it.
            6. Create two lists from the API response:
                - List of CO2 emissions of aircrafts,
                    which have their fuel consumption rate known by the API.
                - List of icao24 codes of aircrafts,
                    which don't have their fuel consumption rate known by the API.
            7. Calculate the CO2 emission of aircrafts with unknown fuel consumption rate.
            8. Sum the CO2 emission of both lists.
            9. Remove aircrafts that are no longer in the airspace.
            10. Remove curr_distance attribute because it should not carry over
                to the next request-response cycle.

        Args:
            states (list): A list of aircraft states received from /states/all endpoint
                of the OpenSky Network API.
            request_time (int): The time that the request was sent in seconds since epoch.
            exit_time_threshold (int): The amount of time needed to determine that
                the  aircraft is no longer in the airspace. Defaults to 60 seconds.

        Returns:
            float: The new carbon emission that was calculated.
        """
        current_aircrafts = self.transform_state_vector(states)
        for aircraft_id, state in current_aircrafts.items():
            if self.aircrafts_in_airspace.get(aircraft_id) is not None:
                old_state = self.aircrafts_in_airspace[aircraft_id]
                old_pos = old_state["position"]
                new_pos = state["position"]

                # calculate distance between previous and current position
                distance = geopy_distance.great_circle(old_pos, new_pos).km
                new_state = {attr: state[attr] for attr in state}
                if distance > 0:
                    new_state["curr_distance"] = distance

                self.aircrafts_in_airspace[aircraft_id] = new_state
            else:
                self.aircrafts_in_airspace[aircraft_id] = state

        # find out which aircrafts are no longer in the airspace
        aircraft_id_not_in_airspace = []
        for aircraft_id in self.aircrafts_in_airspace:
            aircraft = self.aircrafts_in_airspace[aircraft_id]

            # if the last position update was more than x seconds ago,
            # then assume its not in the airspace anymore
            if request_time - aircraft["last_update"] >= exit_time_threshold:
                aircraft_id_not_in_airspace.append(aircraft_id)

        # calculate the distance to edge of bounding box
        # for aircrafts that are no longer in the airspace
        for aircraft_id in aircraft_id_not_in_airspace:
            state = self.aircrafts_in_airspace[aircraft_id]

            if state["on_ground"]:
                continue

            edge_position = self.get_edge_position(
                state["true_track"],
                state["position"],
            )
            # calculate the distance that the aircraft was in the airspace
            distance = geopy_distance.great_circle(
                state["position"],
                (edge_position[0], edge_position[1]),
            ).km

            if distance >= self.bounding_box_diagonal:
                print(
                    f"WARNING: distance is greater than bounding box diagonal\n"
                    f"{self.airspace_name} - {aircraft_id} - "
                    f"true_track: {state['true_track']}, "
                    f"edge position: {edge_position}, old position: {state['position']}\n"
                    f"distance: {distance}"
                )

            if distance > 0:
                self.aircrafts_in_airspace[aircraft_id]["curr_distance"] = distance

        # create icao24_distance_list
        icao24_distance_list = [
            (
                icao24,
                geopy_distance.Distance(kilometers=state["curr_distance"]).nautical,
            )
            for icao24, state in self.aircrafts_in_airspace.items()
            if state.get("curr_distance")
        ]

        new_co2_emission = 0.0

        # call API for aircrafts that have the curr_distance attribute. This could mean:
        # - their position was updated in the current iteration.
        # - have left the airspace + last position was not on ground.
        if icao24_distance_list:
            # get co2 emission from flight fuel consumption API
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

                # calculate co2 emission with unknown fuel consumption rate
                assumed_co2_list = [
                    self.calculate_co2_emission(state["curr_distance"])
                    for icao24, state in self.aircrafts_in_airspace.items()
                    if icao24 in no_co2_icao24_list
                    and state.get("curr_distance") is not None
                ]
                new_co2_emission += sum(co2_list) + sum(assumed_co2_list)
            else:
                print(
                    f"{self.airspace_name} -"
                    f"Using assumed fuel consumption rate for all aircrafts"
                )
                assumed_co2_list = [
                    self.calculate_co2_emission(state["curr_distance"])
                    for icao24, state in self.aircrafts_in_airspace.items()
                    if state.get("curr_distance") is not None
                ]
                new_co2_emission += sum(assumed_co2_list)

        # remove aircrafts no longer in airspace
        for aircraft_id in aircraft_id_not_in_airspace:
            del self.aircrafts_in_airspace[aircraft_id]

        # remove curr_distance for aircrafts in airspace
        for icao24, state in self.aircrafts_in_airspace.items():
            if state.get("curr_distance"):
                del state["curr_distance"]

        return new_co2_emission

    def transform_state_vector(
        self, states: List[List[Any]]
    ) -> Dict[str, Dict[str, Any]]:
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

    def get_edge_position(
        self,
        true_track: float,
        position: Tuple[float, float],
    ) -> Tuple[float, float]:
        """Calculates the bounding box edge position based on the aircraft's true track.

        Args:
            true_track (float): The direction of the aircraft in decimal degrees,
                measured clockwise from north (north = 0).
            position (tuple[float, float]): The geographical coordinates of the aircraft
                in degrees and in the format (latitude, longitude).

        Returns:
            tuple[float, float]: The geographical coordinates (latitude, longitude)
                representing the edge position towards which the aircraft is heading.
        """
        lamin, lomin, lamax, lomax = self.bounding_box

        pos_la, pos_lo = position

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
                edge_pos_lo = lomax

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
        co2_kg = fuel_used_kg * 3.16
        return co2_kg
