import schedule
import time
import json
import os
from threading import Thread
from datetime import datetime
from typing import Callable, Tuple, List, Hashable, Any, Dict
from queue import Queue
from argparse import ArgumentParser

from opensky_network import get_states
from carbon_computation import CarbonComputation
from database import Database, DatabaseError, RedisDatabase


class Worker(Thread):
    """Class to represent a worker thread managing a job queue."""

    def __init__(self) -> None:
        super().__init__()
        self.jobqueue: Queue = Queue()

    def run(self) -> None:
        """Execute all incoming jobs in the job queue."""
        while 1:
            try:
                job_func, args, kwargs = self.jobqueue.get()
                job_func(*args, **kwargs)
                self.jobqueue.task_done()
            except KeyboardInterrupt:
                break


def argparser() -> ArgumentParser:
    """Returns command line arguments parser."""
    parser = ArgumentParser()

    parser.add_argument(
        "--accounts",
        type=str,
        help="Path to the configuration file with opensky account data or json string",
        default="account_data.json",
    )

    parser.add_argument("--db_host", type=str, default="127.0.0.1")

    parser.add_argument("--db_port", type=int, default=6379)

    return parser


def main() -> None:
    """Entry point of the application."""
    args = argparser().parse_args()

    # Read credentials from config file or json-string
    accounts = {}
    if os.path.isfile(args.accounts):
        with open(args.accounts) as json_file:
            accounts = json.load(json_file)
    else:
        accounts = json.loads(args.accounts)

    # Connect to Redis Database
    db = RedisDatabase(host=args.db_host, port=args.db_port)
    try:
        db.is_running()
    except DatabaseError:
        raise RuntimeError("Database connection failed.")

    # Specify bounding boxes for airspaces to be watched
    bounding_boxes = {
        "berlin": (52.3418234221, 13.0882097323, 52.6697240587, 13.7606105539),
        "paris": (48.753020, 2.138901, 48.937837, 2.493896),
        "london": (51.344500, -0.388934, 51.643400, 0.194758),
        "madrid": (40.312817, -3.831991, 40.561061, -3.524374),
    }
    db.set_airspaces(bounding_boxes)

    # Save current time as server startup time
    db.set_server_startup_time(datetime.now())

    # Initialize worker threads for computation
    worker_threads = create_carbon_computer_workers(db, bounding_boxes, accounts)

    # Start worker threads
    for worker_thread in worker_threads:
        worker_thread.start()

    # Start the first carbon caclulation job now instead of waiting 1 minute
    for job in schedule.get_jobs("carbon_computation"):
        job.run()

    # Use schedule
    while True:
        schedule.run_pending()
        time.sleep(1)


def create_carbon_computer_workers(
    db: Database,
    bounding_boxes: Dict[str, Tuple[float, float, float, float]],
    accounts: Dict[str, Dict[str, str]],
) -> List[Worker]:
    """Creates worker threads and provides them with necessary jobs.

    Args:
        db (Database): Database for carbon data storage.
        bounding_boxes (dict[str, Tuple]): A dictionary of bounding boxes of the
            watched airspace.
        accounts (Dict[str, Dict[str, str]]): A dictionary of account information like
            {AIRSPACE: {"username": USERNAME, "password": PASSWORD}, ...}

    Returns:
        List[Worker]: List of worker threads to be started.
    """
    worker_threads = []

    # Create one worker thread for each airspace if username and password were provided
    for airspace, bounding_box in bounding_boxes.items():
        if (
            accounts.get(airspace)
            and accounts[airspace].get("username")
            and accounts[airspace].get("password")
        ):
            carbon_computer = CarbonComputation(airspace, bounding_box)
            worker_thread = Worker()

            # Make carbon computation every minute
            schedule_job_function(
                worker=worker_thread,
                job_func=update_total_co2_emission_job,
                time_unit="minutes",
                interval=1,
                tags=["carbon_computation", carbon_computer.airspace_name],
                db=db,
                username=accounts[airspace].get("username"),
                password=accounts[airspace].get("password"),
                carbon_computer=carbon_computer,
            )

            # Store total carbon value every hour
            schedule_job_function(
                worker=worker_thread,
                job_func=store_co2_emission_job,
                time_unit="hours",
                interval=1,
                tags=["store_emission", carbon_computer.airspace_name],
                db=db,
                carbon_computer=carbon_computer,
            )
            worker_thread.daemon = True
            worker_threads.append(worker_thread)
        else:
            print(f"Missing credentials for {airspace}. Skipping...", flush=True)

    return worker_threads


def schedule_job_function(
    worker: Worker,
    job_func: Callable,
    time_unit: str,
    interval: int,
    tags: List[Hashable] = [],
    *args: Any,
    **kwargs: Any,
) -> None:
    """Schedules a job to be put in a worker thread jobqueue.

    Args:
        worker (Worker): Worker thread that should execute the job at given interval.
        job_func (Callable): Function that should be executed by worker at given interval.
        time_unit (str): The measure of time intervals that the job should be executed.
            Can be seconds, minutes, hours, days or weeks.
        interval (int): The interval at which the scheduled job should be executed.
        tags (List[Hashable]): Tags to mark the scheduled job.
        *args: Positional arguments to be passed to the job function.
        **kwargs: Keyword arguments to be passed to the job function.
    """
    time_mapping = {
        "seconds": schedule.every(interval).seconds,
        "minutes": schedule.every(interval).minutes,
        "hours": schedule.every(interval).hours,
        "days": schedule.every(interval).days,
        "weeks": schedule.every(interval).weeks,
    }

    schedule_func = time_mapping.get(time_unit)

    if schedule_func:
        schedule_func.do(worker.jobqueue.put, (job_func, args, kwargs)).tag(*tags)
    else:
        print("Invalid time unit", flush=True)


def update_total_co2_emission_job(
    db: Database, username: str, password: str, carbon_computer: CarbonComputation
) -> None:
    """Wrapper function for updating the total co2 emission.

    Should be executed as a job by the schedule library.

    Args:
        db (Database): Carbon data storage.
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
        print(
            f"New emission in {carbon_computer.airspace_name}: {new_emission}",
            flush=True,
        )

        # Update total emission
        total_emission = db.get_total_carbon(carbon_computer.airspace_name) + new_emission
        print(
            f"Total emission in {carbon_computer.airspace_name}: {total_emission}",
            flush=True,
        )
        db.set_total_carbon(carbon_computer.airspace_name, total_emission)


def store_co2_emission_job(db: Database, carbon_computer: CarbonComputation) -> None:
    """Stores the hourly carbon emission value in an airspace to a database.

    Args:
        db (Database): Carbon data storage.
        carbon_computer (CarbonComputation): Class instance to handle the computation
            of carbon emission in specific airspace.
    """
    total_value = db.get_total_carbon(carbon_computer.airspace_name)
    db.set_carbon_timestamp(carbon_computer.airspace_name, datetime.now(), total_value)
    print(
        f"Stored total emission in {carbon_computer.airspace_name}: {total_value}",
        flush=True,
    )


if __name__ == "__main__":
    main()
