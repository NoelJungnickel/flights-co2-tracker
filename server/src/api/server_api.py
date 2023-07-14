import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from argparse import ArgumentParser
from typing import Tuple, Dict, Optional
from datetime import datetime

from database import Database, RedisDatabase, DatabaseError


class FastAPIWithDatabase:
    """Basic class managing a FastAPI endpoint with a Redis Database.

    Args:
        db (Database): Database object as data storage.
        host (str): Host address for the FastAPI application. Default: "127.0.0.1".
        port (int): Port for the FastAPI application. Default: 8000.
    """

    def __init__(self, db: Database, host: str = "0.0.0.0", port: int = 8000) -> None:
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

        class CarbonSequenceModel(BaseModel):
            airspace_name: str
            data: Dict[int, float]

        @self.app.get("/api/{airspace}/data", response_model=CarbonSequenceModel)
        async def get_carbon_sequence(
            airspace: str, begin: Optional[int] = None, end: Optional[int] = None
        ) -> CarbonSequenceModel:
            """Return total carbon emmision of given city from database."""
            if begin is None:
                begin = 0
            if end is None:
                end = int(datetime.now().timestamp())
            return CarbonSequenceModel(
                airspace_name=airspace,
                data=self.db.get_carbon_sequence(airspace, begin, end),
            )

        class CelebModel(BaseModel):
            celeb_emission: Dict[str, float]

        @self.app.get("/api/leaderboard", response_model=CelebModel)
        async def get_celeb_emission() -> CelebModel:
            """Return dictionary of celebs with their respective emission."""
            return CelebModel(
                celeb_emission=self.db.get_celeb_emissions()
            )

    def run(self) -> None:
        """Run the FastAPI application with given host and port."""
        uvicorn.run(self.app, host=self.host, port=self.port)


def argparser() -> ArgumentParser:
    """Returns command line arguments parser."""
    parser = ArgumentParser()

    parser.add_argument("--api_host", type=str, default="127.0.0.1")

    parser.add_argument("--api_port", type=int, default=8000)

    parser.add_argument("--db_host", type=str, default="127.0.0.1")

    parser.add_argument("--db_port", type=int, default=6379)

    return parser


def main() -> None:
    """Create and start server-side API."""
    args = argparser().parse_args()
    db = RedisDatabase(args.db_host, args.db_port)

    try:
        db.is_running()
    except DatabaseError:
        raise RuntimeError("Database connection failed.")

    api = FastAPIWithDatabase(db, args.api_host, args.api_port)
    api.run()


if __name__ == "__main__":
    main()
