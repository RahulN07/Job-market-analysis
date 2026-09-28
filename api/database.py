from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import os

DATABASE_URL = os.getenv("DATABASE_URl")

if not DATABASE_URL:
    raise ValueError(" DATABASE_URL is not set in the .env file.")

engine= create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)