import os
import uvicorn

from src.api.server import create_backend

if __name__ == "__main__":
    app = create_backend()
    port = int(os.environ.get("VITE_LEADERBOARD_BACKEND_PORT", "8000"))
    uvicorn.run(app, port=port, host="0.0.0.0", log_level="debug")
