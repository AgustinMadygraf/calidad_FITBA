import os
import uvicorn
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run("servidor.app.main:app", host="0.0.0.0", port=port, reload=True)
