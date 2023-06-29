from abc import ABC, abstractmethod
from redis import Redis


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
