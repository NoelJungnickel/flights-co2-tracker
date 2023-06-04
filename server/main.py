from fastapi import FastAPI
from redis import Redis
import uvicorn


class FastAPIWithRedis:
    """Basic class managing a FastAPI endpoint with a Redis Database.

    Args:
        api_host (str): Host address for the FastAPI application. Default: "127.0.0.1".
        api_port (int): Port for the FastAPI application. Default: 8000.
        redis_host (str): Redis server host address. Default: "127.0.0.1".
        redis_port (int): Redis server port. Default: 6379.
    """

    def __init__(
        self,
        api_host: str = "127.0.0.1",
        api_port: int = 8000,
        redis_host: str = "127.0.0.1",
        redis_port: int = 6379,
    ) -> None:
        self.app = FastAPI()
        self.host = api_host
        self.port = api_port
        # Connecting to Redis Database
        try:
            self.redis = Redis(host=redis_host, port=redis_port, db=0)
            self.redis.info()
        except Exception:
            raise RuntimeError("Failed to connect to Redis.")
        self.register_routes()

    def register_routes(self) -> None:
        """Set specific routes for the FastAPI application."""

        @self.app.get("/api/total/{city}")
        async def get_total_carbon(city: str) -> float:
            total_value = self.redis.hget("total", city)
            return total_value.decode() if total_value else 0.0

    def run(self) -> None:
        """Run the FastAPI application with given host and port."""
        uvicorn.run(self.app, host=self.host, port=self.port)


API_HOST = "127.0.0.1"
API_PORT = 8000
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379

cities = ["berlin"]


def main():
    api = FastAPIWithRedis(API_HOST, API_PORT, REDIS_HOST, REDIS_PORT)
    api.run()


if __name__ == "__main__":
    main()
