import threading
import schedule
import time
from unittest.mock import patch
from calculate_co2 import CarbonComputation
from main import create_carbon_computer_workers
import ctypes


# https://stackoverflow.com/questions/36484151/throw-an-exception-into-another-thread
def ctype_async_raise(target_tid: int, exception: Exception):
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


def mock_update_total_co2_emission_job(username: str, password: str, carbon_computer: CarbonComputation) -> None:
    print(f"Thread {threading.current_thread().ident} - calculating co2 emission")
    time.sleep(2)
    print(f"Thread {threading.current_thread().ident} - finished!")


class TestMain:
    bounding_boxes = {
        "berlin": (52.3418234221, 13.0882097323, 52.6697240587, 13.7606105539),
    }
    usernames = {"berlin": "username"}
    passwords = {"berlin": "heh"}

    # number of running threads should be:
    # thread to run scheduled jobs (the one thats running main) +
    # #cities we're tracking
    @patch("main.update_total_co2_emission_job", wraps=mock_update_total_co2_emission_job)
    def test_correct_number_of_running_threads(self, mock_update_total_co2_emission_job) -> None:
        """Tests the correct number of threads
        
        """
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

    @patch("main.update_total_co2_emission_job", wraps=mock_update_total_co2_emission_job)
    def test_create_correct_num_carbon_computer_workers(
        self, mock_update_total_co2_emission_job
    ) -> None:
        """Checks whether the number of worker threads created is correct.

        One worker thread for every city/bounding box

        """
        bounding_boxes = self.bounding_boxes
        worker_threads = create_carbon_computer_workers(
            bounding_boxes, self.usernames, self.passwords, "seconds", 2
        )
        assert len(worker_threads) == len(bounding_boxes)
