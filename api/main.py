from fastapi import FastAPI
from sqlalchemy import text
from api.database import engine
from fastapi import Query

from api.routes.jobs import router as jobs_router

app = FastAPI(
    title="Job Market Analytics API",
    description="API for exploring global job market data",
    version="1.0.0"
)

@app.get("/")
def home():
    return {"message":"Job Market Analytics API is running"}

@app.get("/health")
def health_check():
    return {"status":"healthly"}

@app.get("/db-health")
def database_health():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"database": "connected"}

app.include_router(jobs_router)

