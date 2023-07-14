import math
from typing import Tuple, Dict, Any
from geopy import distance as geopy_distance  # type: ignore
from flight_fuel_consumption_api import get_flight_fuel_consumption


def get_carbon_by_distance(icao24_distance: Dict[str, float]) -> float:
    """Returns the total carbon emission from flight distances.

    Args:
        icao24_distance (Dict[str, float]): Dictionary of icao24 codes with their
            respective distance travelled.

    Returns:
        float: Total carbon emission in kilograms.
    """
    new_co2_emission = 0.0

    flight_fuels = get_flight_fuel_consumption(icao24_distance)
    if flight_fuels:
        # list of co2 emissions of aircrafts with known fuel consumption
        co2_list = [flight["co2"] for flight in flight_fuels if flight.get("co2")]

        # list of icao24 codes with unknown fuel consumption
        no_co2_icao24_list = [
            flight["icao24"] for flight in flight_fuels if flight.get("co2") is None
        ]

        # calculate co2 emission with unknown fuel consumption rate
        assumed_co2_list = [
            _get_co2_emission_by_consumption_rate(icao24_distance[icao24])
            for icao24 in no_co2_icao24_list
        ]
        new_co2_emission += sum(co2_list) + sum(assumed_co2_list)
    else:
        print("Using assumed fuel consumption rate for all aircrafts")
        assumed_co2_list = [
            _get_co2_emission_by_consumption_rate(distance)
            for icao24, distance in icao24_distance
        ]
        new_co2_emission += sum(assumed_co2_list)

    return new_co2_emission


def _get_co2_emission_by_consumption_rate(
    distance: float, fuel_consumption_rate: float = 3.0
) -> float:
    """Calculates the amount of CO2 emission of a flight.

    Args:
        distance (float): The distance of the (partial-)flight in km.
        fuel_consumption_rate (float): The rate of fuel consumption
            of an aircraft in kilograms per kilometers. Defaults to 3.0 kg/km

    Returns:
        float: The amount of CO2 emission in kilograms.
    """
    fuel_used_kg = fuel_consumption_rate * distance
    co2_kg = fuel_used_kg * 3.16
    return co2_kg


class StateCarbonComputation:
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
        self,
        current_aircrafts: Dict[str, Dict[str, Any]],
        request_time: int,
        exit_time_threshold: int = 300,
    ) -> float:
        """Returns new carbon emission given new airspace state information.

        1. Keep track of the aircraft state from current and previous requests
            and store it in the aircrafts_in_airspace instance variable.
        2. Calculate the distance between the aircraft's previous position and
            its current position, if its previous state is known.
        3. Determine which aircrafts are no longer in the airspace. If said aircraft's
            latest position is on ground, then no further calculations are needed.
            Otherwise, calculate the distance from the latest recorded position to
            the edge of the bounding box.
        4. Create a dict of {icao24 : distance} and compute carbon emission.
        5. Remove aircrafts that are no longer in the airspace.
        6. Remove curr_distance attribute because it should not carry over
            to the next request-response cycle.

        Args:
            current_aircrafts (Dict[str, Dict[str, Any]]): A dictionary of the current
                aircrafts icao with their transformed state vectors in the following form:
                {ICAO24: {
                    "last_update": int,
                    "position": Tuple(float, float),
                    "on_ground": boolean,
                    "velocity": float,
                    "true_track": float,
                }}
            request_time (int): The time that the request was sent in seconds since epoch.
            exit_time_threshold (int): The amount of time needed to determine that
                the  aircraft is no longer in the airspace. Defaults to 300 seconds.

        Returns:
            float: The new carbon emission that was calculated.
        """
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

            edge_position = self._get_edge_position(
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
        icao24_distance = {
            icao24: geopy_distance.Distance(kilometers=state["curr_distance"]).nautical
            for icao24, state in self.aircrafts_in_airspace.items()
            if state.get("curr_distance")
        }

        # get total carbon emission
        new_co2_emission = 0.0
        if icao24_distance:
            new_co2_emission = get_carbon_by_distance(icao24_distance)

        # remove aircrafts no longer in airspace
        for aircraft_id in aircraft_id_not_in_airspace:
            del self.aircrafts_in_airspace[aircraft_id]

        # remove curr_distance for aircrafts in airspace
        for icao24, state in self.aircrafts_in_airspace.items():
            if state.get("curr_distance"):
                del state["curr_distance"]

        return new_co2_emission

    def _get_edge_position(
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
