from fastapi import FastAPI
from redis import Redis
import uvicorn

class FastApiServer:
    def __init__(self, host: str = "127.0.0.1", port: int = "8000") -> None:
        self.app = FastAPI()
        self.host = host
        self.port = port
        self.setup_routes()
        self.start_server()

    def setup_routes(self) -> None:
        @self.app.get("/api/total/berlin")
        async def get_total_emmision_berlin() -> int:
            return 0
            
    def start_server(self) -> None:
        uvicorn.run(self.app, host=self.host, port=self.port)


def main():
    return False


if __name__ == "__main__":
    main()