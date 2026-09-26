import pandas as pd
from sqlalchemy import create_engine, text

# =============================================================================
# CONFIGURATION
# =============================================================================

DATABASE_URL = "postgresql+psycopg2://postgres:1234@localhost:5432/job_market"

PROCESSED_FILE = "data/processed/jobs_cleaned.parquet"

# ============================================================
# LOAD PARQUET
# ============================================================

print("=" * 60)
print("LOADING CLEANED JOB DATA ")
print("=" * 60)

print("\nReading cleaned Parquet file...")

df = pd.read_parquet(PROCESSED_FILE)

print(f"Number of Rows in the cleaned DataFrame:{len(df):,}")
print(f"Number of Columns in the cleaned DataFrame:{len(df.columns):,}")

# ============================================================
# DATABASE CONNECTION
# ============================================================

print("\nConnecting to the database...")

engine= create_engine(DATABASE_URL)

with engine.connect() as connection:
    result = connection.execute(text("SELECT current_database();"))
    database_name = result.scalar()

print(f"Connected to the database: {database_name}")


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading data into postgres database...")

df.to_sql(
    "jobs",
    engine,
    if_exists="append",
    index=False,
    chunksize=1000,
    method="multi"
)

print("\nData loaded succesfully into the databases.")


# ============================================================
# VERIFY
# ============================================================

print("\nVerifying the row count...")

with engine.connect() as connection:
    results = connection.execute(text("SELECT COUNT(*) FROM jobs;"))
    row_count = results.scalar()

print(f"Number of rows in the jobs table: {row_count:,}")

print("\n" + "=" * 70)
print("LOAD COMPLETE")
print("=" * 70)

