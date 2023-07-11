import threading
import schedule
import time
from unittest.mock import patch
from main import create_carbon_computer_workers
import ctypes
import typing
from collections import defaultdict


# https://stackoverflow.com/questions/36484151/throw-an-exception-into-another-thread
@typing.no_type_check
def ctype_async_raise(target_tid, exception):
    """Raises an exception to a specified thread.

    Args:
        target_tid (int): The thread id.
        exception (Exception): The exception to raise.

    """
    ret = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(target_tid), ctypes.py_object(exception)
    )

    if ret == 0:
        raise ValueError("Invalid thread ID")
    elif ret > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(target_tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


@typing.no_type_check
def mock_update_total_co2_emission_job(username, password, carbon_computer):
    """Mocks the update_total_co2_emission_job function."""
    print(f"Thread {threading.current_thread().ident} - calculating co2 emission")
    time.sleep(2)
    print(f"Thread {threading.current_thread().ident} - finished!")


class TestMain:
    """Basic class to group tests on main.py."""

    bounding_boxes = {
        "berlin": (52.3418234221, 13.0882097323, 52.6697240587, 13.7606105539),
        "paris": (48.753020, 2.138901, 48.937837, 2.493896),
        "london": (51.344500, -0.388934, 51.643400, 0.194758),
        "madrid": (40.312817, -3.831991, 40.561061, -3.524374),
    }
    usernames = {
        "berlin": "berlin",
        "paris": "paris",
        "london": "london",
        "madrid": "madrid",
    }
    passwords = {
        "berlin": "bpass",
        "paris": "ppass",
        "london": "lpass",
        "madrid": "mpass",
    }

    @typing.no_type_check
    @patch(
        "main.update_total_co2_emission_job", wraps=mock_update_total_co2_emission_job
    )
    def test_create_correct_workers(self, mock_update_total_co2_emission_job) -> None:
        """Checks whether it creates correct worker threads.

        One worker thread for every airspace/city
        """
        bounding_boxes = self.bounding_boxes
        worker_threads = create_carbon_computer_workers(
            "", bounding_boxes, self.usernames, self.passwords
        )
        for worker_thread in worker_threads:
            worker_thread.start()

        # Test correct number of working threads
        assert threading.active_count() == 1 + len(self.bounding_boxes)

        for worker_thread in worker_threads:
            # raise an exception to worker thread to stop it
            ctype_async_raise(worker_thread.ident, KeyboardInterrupt)

        assert len(worker_threads) == len(bounding_boxes), (
            "Number of worker threads created should equal "
            "to number of airspaces observed"
        )

        # Test if there are two jobs for every airspace
        # and as much computation and storage jobs as number of airspaces
        jobs_per_airspace = defaultdict(int)
        for job in schedule.jobs:
            for airspace in job.tags:
                jobs_per_airspace[airspace] += 1

        assert jobs_per_airspace["carbon_computation"] == len(bounding_boxes.keys())
        assert jobs_per_airspace["store_emission"] == len(bounding_boxes.keys())

        del jobs_per_airspace["carbon_computation"]
        del jobs_per_airspace["store_emission"]

        print(jobs_per_airspace)

        assert set(jobs_per_airspace.keys()) == set(bounding_boxes.keys())

        for airspace, job_count in jobs_per_airspace.items():
            assert job_count == 2
