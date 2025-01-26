import uvicorn

from app.config import logger
from app.main import app as app_instance

if __name__ == "__main__":
    logger.info("Starting server at port 8002")
    uvicorn.run(app_instance, host="0.0.0.0", port=8002)
