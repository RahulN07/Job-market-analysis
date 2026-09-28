
from fastapi import APIRouter, Query
from sqlalchemy import text

from api.database import engine

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("/count")
def get_job_count():
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT COUNT(*) FROM jobs")
        )
        count = result.scalar()

    return {"total_jobs": count}


@router.get("/by-country")
def jobs_by_country():
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT country, COUNT(*) AS job_count
                FROM jobs
                WHERE country IS NOT NULL
                GROUP BY country
                ORDER BY job_count DESC
                LIMIT 10
            """)
        )
        rows = result.mappings().all()

    return {"countries": [dict(row) for row in rows]}


@router.get("/by-work-model")
def jobs_by_work_model():
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT work_model, COUNT(*) AS job_count
                FROM jobs
                WHERE work_model IS NOT NULL
                GROUP BY work_model
                ORDER BY job_count DESC
            """)
        )
        rows = result.mappings().all()

    return {"work_models": [dict(row) for row in rows]}


@router.get("/by-employment-type")
def jobs_by_employment_type():
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT employment_type, COUNT(*) AS job_count
                FROM jobs
                WHERE employment_type IS NOT NULL
                GROUP BY employment_type
                ORDER BY job_count DESC
            """)
        )
        rows = result.mappings().all()

    return {"employment_types": [dict(row) for row in rows]}


@router.get("/salary-summary")
def salary_summary():
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT has_salary, COUNT(*) AS job_count
                FROM jobs
                GROUP BY has_salary
                ORDER BY has_salary DESC
            """)
        )
        rows = result.mappings().all()

    return {"salary_summary": [dict(row) for row in rows]}


@router.get("/salary-reporting-rate")
def salary_reporting_rate():
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT
                    ROUND(
                        100.0 * COUNT(*) FILTER (
                            WHERE has_salary = TRUE
                        ) / NULLIF(COUNT(*), 0),
                        2
                    ) AS salary_reporting_rate
                FROM jobs
            """)
        )
        rate = result.scalar()

    return {"salary_reporting_rate": rate}


@router.get("/search")
def search_job(
    country: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    country = country.strip()

    with engine.connect() as connection:
        count_result = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM jobs
                WHERE LOWER(country) = LOWER(:country)
            """),
            {"country": country}
        )
        total = count_result.scalar()

        result = connection.execute(
            text("""
                SELECT title, country, work_model, employment_type
                FROM jobs
                WHERE LOWER(country) = LOWER(:country)
                ORDER BY title
                LIMIT :limit OFFSET :offset
            """),
            {
                "country": country,
                "limit": limit,
                "offset": offset
            }
        )
        rows = result.mappings().all()

    return {
        "country": country,
        "limit": limit,
        "offset": offset,
        "total": total,
        "jobs": [dict(row) for row in rows]
    }


@router.get("/by-career-level")
def jobs_by_career_level():
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT job_level_normalized, COUNT(*) AS job_count
                FROM jobs
                WHERE job_level_normalized IS NOT NULL
                GROUP BY job_level_normalized
                ORDER BY job_count DESC
            """)
        )
        rows = result.mappings().all()

    return {"career_levels": [dict(row) for row in rows]}


@router.get("/search-by-level")
def search_jobs_by_level(
    level: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    level = level.strip()

    with engine.connect() as connection:
        count_result = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM jobs
                WHERE LOWER(job_level_normalized) = LOWER(:level)
            """),
            {"level": level}
        )
        total = count_result.scalar()

        result = connection.execute(
            text("""
                SELECT title, country, work_model, employment_type,
                       job_level_normalized
                FROM jobs
                WHERE LOWER(job_level_normalized) = LOWER(:level)
                ORDER BY title
                LIMIT :limit OFFSET :offset
            """),
            {
                "level": level,
                "limit": limit,
                "offset": offset
            }
        )
        rows = result.mappings().all()

    return {
        "level": level,
        "limit": limit,
        "offset": offset,
        "total": total,
        "jobs": [dict(row) for row in rows]
    }


@router.get("/salary-statistics")
def salary_statistics():
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT
                    salary_currency,
                    pay_frequency,
                    COUNT(*) AS job_count,
                    ROUND(AVG(salary_min)::numeric, 2)
                        AS avg_salary_min,
                    ROUND(AVG(salary_max)::numeric, 2)
                        AS avg_salary_max
                FROM jobs
                WHERE has_salary = TRUE
                    AND salary_min IS NOT NULL
                    AND salary_max IS NOT NULL
                GROUP BY salary_currency, pay_frequency
                ORDER BY job_count DESC
            """)
        )
        rows = result.mappings().all()

    return {"salary_statistics": [dict(row) for row in rows]}