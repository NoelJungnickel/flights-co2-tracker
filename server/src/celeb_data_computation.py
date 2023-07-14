from typing import TypedDict
from opensky_network import get_flights_of_aircraft_max_24h
import datetime


class Celeb(TypedDict):
    name: str
    icaos: list[str]


def update_all_celebs():
    (
        first_second_yesterday,
        last_second_yesterday,
    ) = get_first_and_last_second_yesterday()

    for celeb in celeb_list:
        for icao in celeb["icaos"]:
            flightResponses = get_flights_of_aircraft_max_24h(
                str(icao),
                first_second_yesterday,
                last_second_yesterday,
                "Noel2",
                "987654321",
            )
            print(f"{celeb=} {icao=}")
            if flightResponses is not None:
                print(f"{flightResponses=}")
                for flightResponse in flightResponses:
                    emis = calculate_co2_emission(
                        flightResponse["lastSeen"] - flightResponse["firstSeen"]
                    )
                    print(f"emis: {emis}kg")
            else:
                print("no data")


def get_first_and_last_second_yesterday() -> tuple[int, int]:
    current_datetime = datetime.datetime.now()

    yesterday = current_datetime - datetime.timedelta(days=1)
    start_of_day = datetime.datetime(
        yesterday.year, yesterday.month, yesterday.day, 0, 0, 0
    )
    end_of_day = datetime.datetime(
        yesterday.year, yesterday.month, yesterday.day, 23, 59, 59
    )

    start_timestamp = int(start_of_day.timestamp())
    end_timestamp = int(end_of_day.timestamp())

    return (start_timestamp, end_timestamp)


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


celeb_list: list[Celeb] = [
    {"name": "Bill Gates", "icaos": ["AC39D6", "A17907"]},
    {"name": "Michael Jordan", "icaos": ["A21FE6"]},
    {"name": "Taylor Swift", "icaos": ["AC64C6"]},
    {"name": "Jim Carrey", "icaos": ["A0F9E7"]},
    {"name": "Alan Sugar", "icaos": ["406B7E"]},
    {"name": "John Travolta", "icaos": ["A96F69"]},
    {"name": "Floyd Mayweather", "icaos": ["A0CF7A"]},
    {"name": "Jay-Z", "icaos": ["A7C582"]},
    {"name": "Steven Spielberg", "icaos": ["AC701E"]},
    {"name": "Kim Kardashian", "icaos": ["A18845"]},
    {"name": "Mark Wahlberg", "icaos": ["A0AEFD"]},
    {"name": "Oprah Winfrey", "icaos": ["A6D9E0"]},
    {"name": "Travis Scott", "icaos": ["A1286D"]},
    {"name": "Tom Cruise", "icaos": ["AB013E"]},
    {"name": "Jeff Bezos", "icaos": ["A2AA92"]},
    {"name": "Kylie Jenner", "icaos": ["AB0A46"]},
    {"name": "Marc Cuban", "icaos": ["ACC306"]},
    {"name": "Elon Musk", "icaos": ["A835AF", "A2AE0A", "A64304"]},
    {"name": "David Geffen", "icaos": ["A1E50A"]},
    {"name": "John Kerry", "icaos": ["A74CC8"]},
    {"name": "Robert Kraft", "icaos": ["A805F0"]},
    {"name": "Ralph Lauren", "icaos": ["A98146"]},
    {"name": "Donald Trump", "icaos": ["AA3410"]},
    {"name": "Jerry Seinfeld", "icaos": ["A9FF1E"]},
    {"name": "Nancy Walton Laurie", "icaos": ["A67552"]},
]

if __name__ == "__main__":
    update_all_celebs()
