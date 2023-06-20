import schedule
import threading
import time
from typing import Callable, Tuple
from redis import Redis
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
        "berlin": (52.3418234221, 13.0882097323, 52.6697240587, 13.7606105539),
    }

    worker_threads = create_carbon_computer_workers(
        bounding_boxes, username, password, "minutes", 1
    )

    for worker_thread in worker_threads:
        worker_thread.start()

    # start the first job now instead of waiting 1 minute
    schedule.run_all()

    # call opensky api every (1 + calculation time) minute(s)
    while True:
        schedule.run_pending()
        time.sleep(1)


def create_carbon_computer_workers(
    bounding_boxes: dict[str, Tuple[float, float, float, float]],
    username: str,
    password: str,
    metric_time: str,
    interval: int,
) -> list[threading.Thread]:
    """Creates worker threads for each city.

    Args:
        bounding_boxes (dict[str, Tuple]): A list of bounding boxes of the
            watched airspace.
        username (str): The username for authentication.
        password (str): The password for authentication.
        carbon_computer (CarbonComputation): Class instance to handle the computation
            of carbon emission in specific airspace.
        metric_time (str): The measure of time intervals. Can be seconds,
            minutes, hours, days or weeks.
        interval (int): The interval at which the scheduled job should be executed

    """

    def schedule_co2_tracking(
        carbon_computer: CarbonComputation, job: Callable, metric_time: str, interval: int
    ) -> None:
        time_mapping = {
            "seconds": schedule.every(interval).seconds,
            "minutes": schedule.every(interval).minutes,
            "hours": schedule.every(interval).hours,
            "days": schedule.every(interval).days,
            "weeks": schedule.every(interval).weeks,
        }

        schedule_func = time_mapping.get(metric_time)
        if schedule_func:
            schedule_func.do(carbon_computer.jobqueue.put, job)
        else:
            print("Invalid metric_time")

    worker_threads = []
    for city in bounding_boxes:
        carbon_computer = CarbonComputation(city, bounding_boxes[city])
        schedule_co2_tracking(
            carbon_computer,
            lambda: (update_total_co2_emission_job(username, password, carbon_computer)),
            metric_time,
            interval,
        )

        # create worker thread for every city
        worker_thread = threading.Thread(target=carbon_computer.worker_main)
        worker_thread.daemon = True
        worker_threads.append(worker_thread)

    return worker_threads


def update_total_co2_emission_job(
    username: str, password: str, carbon_computer: CarbonComputation
) -> None:
    """Wrapper function for updating the total co2 emission.

    Should be executed as a job by the schedule library.

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
