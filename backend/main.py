from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle приложения: запуск и остановка системы чатов."""
    yield


app = FastAPI(
    title="Friends Celendar API",
    description="API для календаря друзей",
    version="1.0.0",
    lifespan=lifespan
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Forwarded-Proto"] = "https"
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def health_check():
    return {"status": "running", "version": "1.0.0"}


# Основные роутеры
app.include_router(auth_router)
