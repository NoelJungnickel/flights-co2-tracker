import schedule
import threading
import time
from redis import Redis
from typing import Callable, Tuple
from argparse import ArgumentParser

from opensky_network import get_states
from calculate_co2 import CarbonComputation

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
redis = Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)


def main() -> None:
    """Entry point of the application."""
    parser = ArgumentParser()
    parser.add_argument("--username", type=str, help="Username for OpenSky")
    parser.add_argument("--password", type=str, help="Password for OpenSky")
    args = parser.parse_args()

    # Access username and password from console
    username = args.username
    password = args.password

    # Connect to Redis Database
    try:
        redis.info()
    except Exception:
        raise RuntimeError("Failed to connect to Redis.")

    bounding_boxes = {
        "berlin": (52.3418234221, 13.0882097323, 52.6697240587, 13.7606105539)
    }

    carbon_berlin = CarbonComputation("berlin", bounding_boxes["berlin"])

    schedule.every(1).minutes.do(
        run_threaded,
        update_total_co2_emission_job,
        args=(username, password, carbon_berlin),
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
    username: str, password: str, carbon_computer: CarbonComputation
) -> None:
    """Wrapper function for updating the total co2 emission.

    Should be executed as a job by the schedule library

    Args:
        username (str): The username for authentication.
        password (str): The password for authentication.
        carbon_computer (CarbonComputation): Class instance to handle the computation
            of carbon emmision in specific airspace.
    """
    response = get_states(username, password, carbon_computer.bounding_box)

    # Compute new emmision (response["states"] can be null)
    if response is not None and response["states"] is not None:
        new_emmision = carbon_computer.get_co2_emission(
            response["states"], response["time"]
        )
    print(f"New Emmision in {carbon_computer.airspace_name}: {new_emmision}")

    # Update total emmision
    total_value = redis.hget("total", carbon_computer.airspace_name)
    total_emmision = (float(total_value.decode()) if total_value else 0.0) + new_emmision
    print(f"Total Emmision in {carbon_computer.airspace_name}: {total_emmision}")
    redis.hset("total", carbon_computer.airspace_name, total_emmision)
