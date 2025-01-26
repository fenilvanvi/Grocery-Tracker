from fastapi import FastAPI

from app.routers.tracker import router

app = FastAPI()

app.include_router(router)
