import uvicorn

from src.interface_adapter.controller.api.app.main import app
from src.interface_adapter.controller.api.app.settings import settings

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.port)
