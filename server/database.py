from abc import ABC, abstractmethod
from redis import Redis
from typing import Tuple
import json

from celeb_data_computation import Celeb


class DatabaseError(Exception):
    """Class providing a basic db error.

    Args:
        message (str): Error message to be returned.
    """

    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(f"Database Error: {message}")


class Database(ABC):
    """Abstract class for database providing the neccessary functions."""

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port

    @abstractmethod
    def is_running(self) -> None:
        """Check whether database is running.

        Raises:
            DatabaseError, if connection cannot be made.
        """
        pass

    @abstractmethod
    def get_total_carbon(self, airspace: str) -> float:
        """Returns total carbon emission value in airspace."""
        pass

    @abstractmethod
    def set_total_carbon(self, airspace: str, value: float) -> None:
        """Sets total carbon emission value in airspace."""
        pass

    @abstractmethod
    def store_hourly_carbon(self, airspace: str, value: Tuple[int, float]) -> None:
        """Stores the hourly carbon emission value in an airspace.

        Args:
            airspace (str): Name of the observed airspace.
            value (Tuple[int, float]): Tuple of time in seconds since epoch
                and carbon emission value.
        """
        pass

    @abstractmethod
    def get_celeb_carbon(self, celeb: Celeb) -> float:
        """Returns carbon emission of given celebrity for the current month."""
        pass

    @abstractmethod
    def increment_celeb_carbon(self, celeb: Celeb, amount: float) -> float:
        """Sets carbon emission of given celebrity.

        Args:
            celeb (Celeb): Celebrity object to update
            amount (float): Amount to increment carbon emission of given celeb

        Returns:
            float: Amount of carbon emission after incrementing
        """
        pass

    @abstractmethod
    def clear_celeb_carbon(self, celeb: Celeb) -> bool:
        """Clears carbon emission of given celebrity and returns boolean indicating success."""
        pass


class RedisDatabase(Database):
    """Implementation of database functions with a redis Database."""

    def __init__(self, host: str, port: int) -> None:
        super().__init__(host, port)
        self.redis = Redis(host=host, port=port, db=0)

    def is_running(self) -> None:
        """Check whether redis is running.

        Raises:
            DatabaseError, if connection cannot be made.
        """
        try:
            self.redis.info()
        except Exception:
            raise DatabaseError("Redis Database not running.")

    def get_total_carbon(self, airspace: str) -> float:
        """Return total carbon emmision of given airspace from redis."""
        total_value = self.redis.hget("total", airspace)
        return float(total_value.decode()) if total_value else 0.0

    def set_total_carbon(self, airspace: str, value: float) -> None:
        """Sets total carbon emission value in airspace."""
        self.redis.hset("total", airspace, value)

    def store_hourly_carbon(self, airspace: str, value: Tuple[int, float]) -> None:
        """Stores the hourly carbon emission value in an airspace."""
        record = {"time": value[0], "co2": value[1]}
        hourly_carbon_records_bytes = self.redis.hget("hourly", airspace)
        if hourly_carbon_records_bytes is None:
            self.redis.hset("hourly", airspace, json.dumps([record]))
            return

        hourly_carbon_records = json.loads(hourly_carbon_records_bytes.decode())
        hourly_carbon_records.append(record)
        print(f"Hourly Carbon - {airspace}: {hourly_carbon_records}")
        self.redis.hset("hourly", airspace, json.dumps(hourly_carbon_records))

    def get_celeb_carbon(self, celeb: Celeb) -> float:
        celeb_carbon = self.redis.hget(celeb["name"], "emissionsThisMonth")
        return float(celeb_carbon.decode()) if celeb_carbon else 0.0

    def increment_celeb_carbon(self, celeb: Celeb, amount: float) -> float:
        new_amount = self.redis.hincrbyfloat(
            celeb["name"], "emissionsThisMonth", amount
        )
        return new_amount

    def clear_celeb_carbon(self, celeb: Celeb) -> bool:
        result = self.redis.hset(celeb["name"], "emissionsThisMonth", 0.0)
        return bool(result)
