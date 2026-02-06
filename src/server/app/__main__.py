import uvicorn

from src.server.app.main import app
from src.server.app.settings import settings

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.port)
