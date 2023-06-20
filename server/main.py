import schedule
import threading
import time
import configparser
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
    parser.add_argument("--config", type=str, help="Path to the configuration file")
    args = parser.parse_args()

    config_path = args.config

    # Read credentials from config file
    usernames = {}
    passwords = {}

    config = configparser.ConfigParser()
    config.read(config_path)

    for section in config.sections():
        if "username" in config[section] and "password" in config[section]:
            username = config[section]["username"]
            password = config[section]["password"]
            usernames[section] = username
            passwords[section] = password

    # Connect to Redis Database
    try:
        redis.info()
    except Exception:
        raise RuntimeError("Failed to connect to Redis.")

    # Specify bounding boxes for airspaces to be watched
    bounding_boxes = {
        "berlin": (52.3418234221, 13.0882097323, 52.6697240587, 13.7606105539),
        "paris": (48.753020, 2.138901, 48.937837, 2.493896),
        #"london": (51.344500, -0.388934, 51.643400, 0.194758),
        #"madrid": (40.312817, -3.831991, 40.561061, -3.524374)
    }

    # Iterate over the bounding boxes and schedule a separate thread for each box
    for city, bounding_box in bounding_boxes.items():
        username = usernames.get(city)
        password = passwords.get(city)

        if username and password:
            carbon_computation = CarbonComputation(city, bounding_box)
            schedule.every(1).minutes.do(
                run_threaded,
                update_total_co2_emission_job,
                args=(username, password, carbon_computation),
            )
        else:
            print(f"Missing credentials for {city}. Skipping...")

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
            of carbon emission in specific airspace.
    """
    response = get_states(username, password, carbon_computer.bounding_box)

    # Compute new emission (response["states"] can be null)
    if response is not None and response["states"] is not None:
        new_emission = carbon_computer.get_co2_emission(
            response["states"], response["time"]
        )
        print(f"New emission in {carbon_computer.airspace_name}: {new_emission}")

        # Update total emission
        total_value = redis.hget("total", carbon_computer.airspace_name)
        total_emission = (
            float(total_value.decode()) if total_value else 0.0
        ) + new_emission
        print(f"Total emission in {carbon_computer.airspace_name}: {total_emission}")
        redis.hset("total", carbon_computer.airspace_name, total_emission)


if __name__ == "__main__":
    main()
