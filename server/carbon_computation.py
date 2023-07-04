from geopy import distance as geopy_distance  # type: ignore
import math
from typing import Tuple, Dict, Any, List


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

    def get_co2_emission(
        self, states: List[List[Any]], exit_time_threshold: int = 120
    ) -> float:
        """Returns new carbon emission given new airspace state information.

            1. Brings the states vector to a better representation containing the useful
                information for each aircraft in a dictionary
            2. Calculates the carbon emission for all aircrafts that did not leave the
                airspace since the last time data was received.
            3. Calculates the carbon emission for all aircrfts that die leave our
                airspace since the last time data was received by estimating the duration
                it spend in the watched airspace.
            4. Update the airspace data class variable to the reflect the current airspace
                data

        Args:
            states (list): A list of aircraft states received from /states/all endpoint
                of the OpenSky Network API.
            exit_time_threshold (int): The amount of time needed to determine that
                the  aircraft is no longer in the airspace. Defaults to 60 seconds.

        Returns:
            float: The new carbon emission that was calculated.
        """
        current_aircrafts = self.transform_state_vector(states)

        new_co2_emission = 0.0

        # Compute carbon emission for aircrafts, which did not leave the airspace
        aircraft_ids_still_in_airspace = list(
            set(current_aircrafts.keys()) & set(self.aircrafts_in_airspace.keys())
        )
        for aircraft_id in aircraft_ids_still_in_airspace:
            aircraft = self.aircrafts_in_airspace[aircraft_id]
            duration = self.calculate_duration(
                old_pos=aircraft["position"],
                new_pos=current_aircrafts[aircraft_id]["position"],
                velocity=aircraft["velocity"],
            )
            new_co2_emission += self.calculate_co2_emission(duration)

        # Compute carbon emission for aircrafts, which did leave the airspace
        aircraft_ids_not_in_airspace = list(
            set(self.aircrafts_in_airspace.keys()) - set(current_aircrafts.keys())
        )
        for aircraft_id in aircraft_ids_not_in_airspace:
            aircraft = self.aircrafts_in_airspace[aircraft_id]
            duration = self.calculate_duration(
                old_pos=aircraft["position"],
                new_pos=self.get_edge_position(
                    aircraft["true_track"], aircraft["position"]
                ),
                velocity=aircraft["velocity"],
            )
            new_co2_emission += self.calculate_co2_emission(duration)

        self.aircrafts_in_airspace = current_aircrafts

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
                    "position": (state[6], state[5]),
                    "on_ground": state[8],
                    "velocity": state[9],
                    "true_track": state[10],
                }
        return current_aircrafts

    def calculate_duration(
        self, old_pos: Tuple[float, float], new_pos: Tuple[float, float], velocity: float
    ) -> float:
        """Calculates duration of travel from one point to another with constant velocity.

        Args:
            old_pos (tuple[float,float]): The first geographical point in degrees and
                in the format (latitude, longitude).
            new_pos (tuple[float, float]): The second geographical point in degrees and
                in the format (latitude, longitude).
            velocity (float): The speed of the aircraft in meters per second.

        Returns:
            float: The duration in seconds to travel from old_pos to new_pos with
                constant velocity.
        """
        if velocity == 0:
            return 0.0

        # Get the distance between the two points in kilometers
        distance = geopy_distance.great_circle(old_pos, new_pos).km
        # Calculate the time required to travel the distance at the given velocity.
        time = (distance * 1000) / velocity
        return time

    def get_edge_position(
        self,
        true_track: float,
        position: Tuple[float, float],
    ) -> Tuple[float, float]:
        """Calculates the distance to the bounding box edge.

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
        self, duration: float, fuel_consumption_rate: float = 378.54
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
