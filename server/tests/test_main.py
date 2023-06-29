import threading
import schedule
import time
from unittest.mock import patch
from main import create_carbon_computer_workers
import ctypes
import typing


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

    # number of running threads should be:
    # thread to run scheduled jobs (the one thats running main) +
    # #cities we're tracking
    @typing.no_type_check
    @patch("main.update_total_co2_emission_job", wraps=mock_update_total_co2_emission_job)
    def test_correct_number_of_running_threads(self, mock_update_total_co2_emission_job):
        """Tests the correct number of threads."""
        bounding_boxes = self.bounding_boxes

        worker_threads = create_carbon_computer_workers(
            bounding_boxes, self.usernames, self.passwords, "seconds", 2
        )
        for worker_thread in worker_threads:
            worker_thread.start()

        schedule.run_all()

        count = 0
        while True:
            schedule.run_pending()

            if count == 10:
                break
            time.sleep(1)
            count += 1

        assert threading.active_count() == 1 + len(self.bounding_boxes)
        for worker_thread in worker_threads:
            # raise an exception to worker thread to stop it
            ctype_async_raise(worker_thread.ident, KeyboardInterrupt)

    @typing.no_type_check
    @patch("main.update_total_co2_emission_job", wraps=mock_update_total_co2_emission_job)
    def test_create_correct_workers(self, mock_update_total_co2_emission_job) -> None:
        """Checks whether it creates correct worker threads.

        One worker thread for every airspace/city
        """

        def run_jobs():
            while 1:
                try:
                    print(f"{threading.current_thread().name} - running pending jobs")
                    schedule.run_pending()
                    time.sleep(1)
                except KeyboardInterrupt:
                    break

        bounding_boxes = self.bounding_boxes
        worker_threads = create_carbon_computer_workers(
            bounding_boxes, self.usernames, self.passwords, "seconds", 2
        )
        for worker_thread in worker_threads:
            worker_thread.start()

        schedule.run_all()
        # run pending jobs in a separate thread
        job_runner_thread = threading.Thread(name="job_runner", target=run_jobs)
        job_runner_thread.start()

        time.sleep(2)
        airspace_names = []

        # get the carbon computer and its airspace name in the job
        # a job should be created for every airspace
        for job in schedule.get_jobs():
            create_update_total_co2_emission_job = job.job_func.args[0]
            create_update_total_co2_emission_job_args = (
                create_update_total_co2_emission_job.__defaults__[0]
            )
            carbon_computer = create_update_total_co2_emission_job_args[2]
            airspace_names.append(carbon_computer.airspace_name)

        for worker_thread in worker_threads:
            # raise an exception to worker thread to stop it
            ctype_async_raise(worker_thread.ident, KeyboardInterrupt)
        ctype_async_raise(job_runner_thread.ident, KeyboardInterrupt)

        assert len(worker_threads) == len(bounding_boxes), (
            "Number of worker threads created should equal "
            "to number of airspaces observed"
        )
        assert set(airspace_names) == set(
            bounding_boxes.keys()
        ), "Incorrect carbon computers created for airspaces observed"
