# Global Job Market Analytics Platform

An end-to-end data analytics project that analyzes global job postings to explore hiring trends, employment types, work models, career levels, and salary reporting.

## Project Overview

This project processes over 112,000 job postings using Python and PostgreSQL, analyzes the data with SQL, and presents insights through a Power BI dashboard. A FastAPI application exposes the analytics through REST API endpoints, and Docker provides a containerized environment.

## Tech Stack

* **Programming:** Python 3.13, SQL
* **Data Processing:** Pandas, PyArrow
* **Database:** PostgreSQL
* **API:** FastAPI, SQLAlchemy
* **Visualization:** Power BI
* **Containerization:** Docker
* **Version Control:** Git, GitHub

## Key Features

* Extracts and processes a dataset containing 112,816 job postings.
* Cleans and transforms job titles, employment types, work models, and salary fields.
* Loads processed data into PostgreSQL.
* Uses SQL to analyze job postings by country, career level, employment type, and work model.
* Provides a Power BI dashboard with interactive visualizations and KPI cards.
* Exposes analytics through FastAPI REST endpoints.
* Includes Swagger API documentation.
* Runs the API in a Docker container.

## Project Structure

```text
job-market-analytics/
├── api/
│   ├── main.py
│   ├── database.py
│   └── routes/
│       ├── __init__.py
│       └── jobs.py
├── analytics/
│   └── queries.sql
├── data/
│   ├── raw/
│   └── processed/
├── etl/
│   ├── extract.py
│   └── load.py
├── database/
├── dashboard/
├── tests/
├── Dockerfile
├── .dockerignore
├── .gitignore
├── requirements.txt
└── README.md
```

## API Endpoints

| Endpoint                      | Description                                     |
| ----------------------------- | ----------------------------------------------- |
| `/health`                     | Check API health                                |
| `/db-health`                  | Check database connection                       |
| `/jobs/count`                 | Get total job postings                          |
| `/jobs/by-country`            | Job postings by country                         |
| `/jobs/by-work-model`         | Job postings by work model                      |
| `/jobs/by-employment-type`    | Job postings by employment type                 |
| `/jobs/by-career-level`       | Job postings by career level                    |
| `/jobs/salary-summary`        | Summary of salary availability                  |
| `/jobs/salary-reporting-rate` | Salary reporting rate                           |
| `/jobs/search`                | Search jobs by country                          |
| `/jobs/search-by-level`       | Search jobs by career level                     |
| `/jobs/salary-statistics`     | Salary statistics by currency and pay frequency |

Interactive API documentation is available at `/docs` when the API is running.

## Running the API Locally

### 1. Clone the repository

```bash
git clone https://github.com/RahulN07/job-market-analytics.git
cd job-market-analytics
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the database

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/job_market
```

Replace `YOUR_PASSWORD` with your PostgreSQL password. Ensure the `job_market` database and `jobs` table are available.

### 5. Start the API

```bash
uvicorn api.main:app --reload
```

Open `http://127.0.0.1:8000/docs` to explore the API.

## Running with Docker

Make sure Docker Desktop is running and PostgreSQL is accessible from the container.

Build the image:

```bash
docker build -t job-market-api .
```

Run the container:

```bash
docker run -d --name job-market-container -p 8000:8000 --env-file .env job-market-api
```

For Docker Desktop on Windows, configure the database URL to use `host.docker.internal` instead of `localhost`.

Check the container logs:

```bash
docker logs job-market-container
```

Stop the container:

```bash
docker stop job-market-container
```

## Dashboard

The Power BI dashboard presents job market insights, including:

* Job postings by country
* Work model distribution
* Employment type distribution
* Career level distribution
* Salary reporting rates
* Total job postings and salary availability KPIs

![Global Job Market Analytics Dashboard](dashboard/screenshots/dashboard_overview.png)

## Data Source

Dataset: NextGig — Global Job Postings Multi-ATS.

The dataset contains job postings collected from multiple applicant tracking systems. The project uses a local copy of the dataset for analysis.

## Future Improvements

* Add automated data quality tests.
* Add more advanced job market insights.
* Improve salary analysis by accounting for currencies and pay frequencies.
* Deploy the API to a cloud platform.
* Add automated ETL scheduling.

## Author

**Rahul Nayak**
Computer Science Engineering Graduate | Python Developer | Data Engineering

GitHub: [RahulN07](https://github.com/RahulN07)
