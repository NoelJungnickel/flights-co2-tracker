from fastapi import FastAPI
from pydantic import BaseModel
from typing import Tuple, Dict

from database import Database


class FastAPIWithDatabase:
    """Basic class managing a FastAPI endpoint with a Redis Database.

    Args:
        db (Database): Database object as data storage.
        host (str): Host address for the FastAPI application. Default: "127.0.0.1".
        port (int): Port for the FastAPI application. Default: 8000.
    """

    def __init__(self, db: Database, host: str = "127.0.0.1", port: int = 8000) -> None:
        self.app = FastAPI()
        self.host = host
        self.port = port
        self.db = db
        self.register_routes()

    def register_routes(self) -> None:
        """Set specific routes for the FastAPI application."""

        class ServerStartModel(BaseModel):
            timestamp: int

        @self.app.get("/api/serverstart", response_model=ServerStartModel)
        async def get_server_startup_time() -> ServerStartModel:
            """Return total carbon emmision of given city from database."""
            print("j")
            return ServerStartModel(timestamp=self.db.get_server_startup_time())

        class AirspaceModel(BaseModel):
            airspaces: Dict[str, Tuple]

        @self.app.get("/api/airspaces", response_model=AirspaceModel)
        async def get_airspaces() -> AirspaceModel:
            """Return all supported airspaces with bounding boxes."""
            return AirspaceModel(airspaces=self.db.get_airspaces())

        class TotalCarbonModel(BaseModel):
            airspace_name: str
            total: float

        @self.app.get("/api/{airspace}/total", response_model=TotalCarbonModel)
        async def get_total_carbon(airspace: str) -> TotalCarbonModel:
            """Return total carbon emmision of given city from database."""
            return TotalCarbonModel(
                airspace_name=airspace, total=self.db.get_total_carbon(airspace)
            )
