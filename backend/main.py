import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import init_db
from routes.tools import router as tools_router
from routes.conversations import router as conversations_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title=os.getenv("APP_NAME", "Backend API"), lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tools_router)
app.include_router(conversations_router)


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI", "app_name": os.getenv("APP_NAME")}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
