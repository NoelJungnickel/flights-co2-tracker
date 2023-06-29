from fastapi import FastAPI

from database import Database


class FastAPIWithDatabase:
    """Basic class managing a FastAPI endpoint with a Redis Database.

    Args:
        db (Database): Database object as data storage.
        api_host (str): Host address for the FastAPI application. Default: "127.0.0.1".
        api_port (int): Port for the FastAPI application. Default: 8000.
    """

    def __init__(self, db: Database, host: str = "127.0.0.1", port: int = 8000) -> None:
        self.app = FastAPI()
        self.host = host
        self.port = port
        self.db = db
        self.register_routes()

    def register_routes(self) -> None:
        """Set specific routes for the FastAPI application."""

        @self.app.get("/api/total/{airspace}")
        async def get_total_carbon(airspace: str) -> float:
            """Return total carbon emmision of given city from database."""
            return self.db.get_total_carbon(airspace)
