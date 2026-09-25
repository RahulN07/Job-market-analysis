import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# JOB MARKET ANALYTICS PLATFORM
# COMPLETE DATA EXTRACTION + CLEANING + TRANSFORMATION PIPELINE
# ============================================================
#
# RAW DATA
#     ↓
# LOAD
#     ↓
# COPY RAW DATA
#     ↓
# GENERAL TEXT CLEANING
#     ↓
# WORK MODEL
#     ↓
# EMPLOYMENT TYPE
#     ↓
# TITLE QUALITY CHECK
#     ↓
# DATE POSTED
#     ↓
# CLOSING DATE
#     ↓
# DATE FEATURES
#     ↓
# SALARY
#     ↓
# LOCATION
#     ↓
# EXPERIENCE
#     ↓
# EDUCATION
#     ↓
# BOOLEAN FIELDS
#     ↓
# TRAVEL
#     ↓
# ANALYTICS FLAGS
#     ↓
# DUPLICATE CHECK
#     ↓
# VALIDATION
#     ↓
# SAVE PARQUET + CSV
#     ↓
# VERIFY SAVED FILE
#
# IMPORTANT:
#
# jobs         = ORIGINAL RAW DATA
# cleaned_jobs = CLEANED + TRANSFORMED DATA
#
# Raw data is NEVER modified.
# ============================================================


# ============================================================
# 1. FILE PATHS
# ============================================================

RAW_FILE = Path(
    "data/raw/nextgig_jobs_2026-06.parquet"
)

PROCESSED_DIR = Path(
    "data/processed"
)

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)

PROCESSED_FILE = (
    PROCESSED_DIR /
    "jobs_cleaned.parquet"
)

CSV_FILE = (
    PROCESSED_DIR /
    "jobs_cleaned.csv"
)


# ============================================================
# 2. LOAD RAW DATA
# ============================================================

print("\n" + "=" * 70)
print("1. LOADING RAW DATA")
print("=" * 70)

jobs = pd.read_parquet(
    RAW_FILE,
    engine="pyarrow"
)

print(
    "Raw shape:",
    jobs.shape
)

print(
    "Raw rows:",
    len(jobs)
)

print(
    "Raw columns:",
    len(jobs.columns)
)


# ============================================================
# 3. CREATE CLEANED COPY
# ============================================================

print("\n" + "=" * 70)
print("2. CREATING CLEANED COPY")
print("=" * 70)

# Never modify the original dataframe.
cleaned_jobs = jobs.copy()

print(
    "Cleaned copy created."
)


# ============================================================
# 4. GENERAL TEXT CLEANING
# ============================================================

print("\n" + "=" * 70)
print("3. GENERAL TEXT CLEANING")
print("=" * 70)

object_columns = cleaned_jobs.select_dtypes(
    include=["object", "string"]
).columns

for column in object_columns:

    cleaned_jobs[column] = (
        cleaned_jobs[column]
        .astype("string")
        .str.strip()
    )

    cleaned_jobs[column] = (
        cleaned_jobs[column]
        .replace("", pd.NA)
    )

print(
    "Text columns cleaned:",
    len(object_columns)
)


# ============================================================
# 5. WORK MODEL CLEANING
# ============================================================

print("\n" + "=" * 70)
print("4. WORK MODEL CLEANING")
print("=" * 70)

work_model_mapping = {

    "on-site": "On-site",
    "On-Site": "On-site",
    "ON-SITE": "On-site",
    "onsite": "On-site",
    "Onsite": "On-site",
    "ON_SITE": "On-site",

    # Unicode non-breaking hyphen variant
    "On‑site": "On-site",

    # Unknown / invalid value
    "??": "Unknown",
}

cleaned_jobs["work_model"] = (
    cleaned_jobs["work_model"]
    .replace(work_model_mapping)
)

print(
    cleaned_jobs["work_model"]
    .value_counts(dropna=False)
)


# ============================================================
# 6. EMPLOYMENT TYPE CLEANING
# ============================================================

print("\n" + "=" * 70)
print("5. EMPLOYMENT TYPE CLEANING")
print("=" * 70)


# ------------------------------------------------------------
# 6A. Normalize obvious single-value variants
# ------------------------------------------------------------

employment_mapping = {

    "Full-": "Full-time",
    "Full-Time": "Full-time",
    "FULL_TIME": "Full-time",
    "Fullt": "Full-time",
    "Fulltime": "Full-time",
    "Full...": "Full-time",

    "Part-": "Part-time",
    "Part-Time": "Part-time",
    "PART_TIME": "Part-time",
    "Part time": "Part-time",
    "Part Time": "Part-time",
    "Parttime": "Part-time",
}

cleaned_jobs["employment_type"] = (
    cleaned_jobs["employment_type"]
    .replace(employment_mapping)
)


# ------------------------------------------------------------
# 6B. Convert pipe-separated values
# ------------------------------------------------------------

cleaned_jobs["employment_type"] = (
    cleaned_jobs["employment_type"]
    .str.replace(
        "|",
        ",",
        regex=False
    )
)


# ------------------------------------------------------------
# 6C. Normalize comma spacing
# ------------------------------------------------------------

cleaned_jobs["employment_type"] = (
    cleaned_jobs["employment_type"]
    .str.replace(
        r",\s*",
        ", ",
        regex=True
    )
)


# ------------------------------------------------------------
# 6D. Normalize capitalization inside multi-value cells
# ------------------------------------------------------------

cleaned_jobs["employment_type"] = (
    cleaned_jobs["employment_type"]
    .str.replace(
        "Full-Time",
        "Full-time",
        regex=False
    )
    .str.replace(
        "Part-Time",
        "Part-time",
        regex=False
    )
)


# ------------------------------------------------------------
# 6E. Exact variant
# ------------------------------------------------------------

cleaned_jobs["employment_type"] = (
    cleaned_jobs["employment_type"]
    .replace(
        {
            "Temporary Part-Time":
                "Temporary Part-time"
        }
    )
)


# ------------------------------------------------------------
# 6F. Known data-quality correction
# ------------------------------------------------------------

cleaned_jobs.loc[
    cleaned_jobs["title"]
    == "Warehouse Operator (contratto a tempo determinato 12 mesi)",
    "employment_type"
] = "Contract"


# ------------------------------------------------------------
# 6G. Unknown employment type
# ------------------------------------------------------------

cleaned_jobs.loc[
    cleaned_jobs["title"]
    == "Registered Nurse (Med Surg)",
    "employment_type"
] = "Unknown"


print(
    cleaned_jobs["employment_type"]
    .value_counts(dropna=False)
)


# ============================================================
# 7. TITLE QUALITY CHECK
# ============================================================

print("\n" + "=" * 70)
print("6. TITLE QUALITY CHECK")
print("=" * 70)

full_time_title_count = (
    cleaned_jobs["title"]
    .eq("Full-time")
    .sum()
)

missing_title_count = (
    cleaned_jobs["title"]
    .isna()
    .sum()
)

total_rows = len(
    cleaned_jobs
)

print(
    "Total rows:",
    total_rows
)

print(
    "Full-time used as title:",
    full_time_title_count
)

print(
    "Percentage:",
    round(
        (
            full_time_title_count /
            total_rows
        ) * 100,
        2
    ),
    "%"
)

print(
    "Missing titles:",
    missing_title_count
)

print(
    "\nSuspicious title examples:"
)

print(
    cleaned_jobs.loc[
        cleaned_jobs["title"] == "Full-time",
        [
            "title",
            "normalized_title",
            "function",
            "occupational_category",
            "job_level_normalized",
            "company_name"
        ]
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# 8. TOP JOB TITLES
# ============================================================

print("\n" + "=" * 70)
print("7. TOP 20 JOB TITLES")
print("=" * 70)

print(
    cleaned_jobs["title"]
    .value_counts()
    .head(20)
)


# ============================================================
# 9. DATE_POSTED CLEANING
# ============================================================

print("\n" + "=" * 70)
print("8. DATE_POSTED CLEANING")
print("=" * 70)

raw_dates = (
    jobs["date_posted"]
    .copy()
)

date_strings = (
    raw_dates
    .astype("string")
    .str.strip()
)


# ------------------------------------------------------------
# Known placeholders / clearly invalid values
# ------------------------------------------------------------

date_strings = date_strings.replace(
    {
        "": pd.NA,
        "MM/DD/YYYY": pd.NA,
        "Posted Yesterday": pd.NA,
        "12 months": pd.NA,
        "6 months": pd.NA,
        "Behavior Technician": pd.NA,
        "Order-to-Cash": pd.NA,
        "36": pd.NA,
        "00/00/2026": pd.NA,
    }
)


# ------------------------------------------------------------
# Create empty datetime Series
# ------------------------------------------------------------

clean_date = pd.Series(
    pd.NaT,
    index=jobs.index,
    dtype="datetime64[ns]"
)


# ------------------------------------------------------------
# Supported date formats
# ------------------------------------------------------------

date_formats = [

    "%m/%d/%Y",

    "%Y-%m-%d",

    "%m/%d/%y",

    "%d/%m/%Y",

    "%Y/%m/%d",

]


for date_format in date_formats:

    remaining = (
        date_strings.notna()
        &
        clean_date.isna()
    )

    clean_date.loc[remaining] = (
        pd.to_datetime(
            date_strings.loc[remaining],
            format=date_format,
            errors="coerce"
        )
    )


# ------------------------------------------------------------
# Handle timestamps
#
# Example:
# 05/06/2026 09:50
# ------------------------------------------------------------

remaining = (
    date_strings.notna()
    &
    clean_date.isna()
)

clean_date.loc[remaining] = (
    pd.to_datetime(
        date_strings.loc[remaining],
        format="%m/%d/%Y %H:%M",
        errors="coerce"
    )
)


cleaned_jobs["date_posted"] = (
    clean_date
)


print(
    "Original missing:",
    raw_dates.isna().sum()
)

print(
    "Original non-missing:",
    raw_dates.notna().sum()
)

print(
    "Successfully parsed:",
    cleaned_jobs["date_posted"].notna().sum()
)

print(
    "Final missing:",
    cleaned_jobs["date_posted"].isna().sum()
)

print(
    "Data type:",
    cleaned_jobs["date_posted"].dtype
)


# ------------------------------------------------------------
# Remaining invalid date values
# ------------------------------------------------------------

remaining_bad_dates = jobs.loc[
    jobs["date_posted"].notna()
    &
    cleaned_jobs["date_posted"].isna(),
    "date_posted"
]

print(
    "\nRemaining invalid date_posted values:"
)

print(
    remaining_bad_dates
    .value_counts()
    .head(50)
)


# ============================================================
# 10. CLOSING_DATE CLEANING
# ============================================================

print("\n" + "=" * 70)
print("9. CLOSING_DATE CLEANING")
print("=" * 70)

raw_closing_dates = (
    jobs["closing_date"]
    .copy()
)

closing_strings = (
    raw_closing_dates
    .astype("string")
    .str.strip()
)

parsed_closing_dates = pd.Series(
    pd.NaT,
    index=jobs.index,
    dtype="datetime64[ns]"
)

closing_formats = [

    "%m/%d/%Y",

    "%Y-%m-%d",

    "%m/%d/%y",

    "%d/%m/%Y",

    "%Y/%m/%d",

]


for date_format in closing_formats:

    remaining = (
        closing_strings.notna()
        &
        parsed_closing_dates.isna()
    )

    parsed_closing_dates.loc[remaining] = (
        pd.to_datetime(
            closing_strings.loc[remaining],
            format=date_format,
            errors="coerce"
        )
    )


# ------------------------------------------------------------
# Handle timestamps
# ------------------------------------------------------------

remaining = (
    closing_strings.notna()
    &
    parsed_closing_dates.isna()
)

parsed_closing_dates.loc[remaining] = (
    pd.to_datetime(
        closing_strings.loc[remaining],
        format="%m/%d/%Y %H:%M",
        errors="coerce"
    )
)

cleaned_jobs["closing_date"] = (
    parsed_closing_dates
)

print(
    "Original missing:",
    raw_closing_dates.isna().sum()
)

print(
    "Original non-missing:",
    raw_closing_dates.notna().sum()
)

print(
    "Successfully parsed:",
    cleaned_jobs["closing_date"].notna().sum()
)

print(
    "Final missing:",
    cleaned_jobs["closing_date"].isna().sum()
)

print(
    "Data type:",
    cleaned_jobs["closing_date"].dtype
)


# ------------------------------------------------------------
# Remaining invalid closing dates
# ------------------------------------------------------------

bad_closing_dates = jobs.loc[
    jobs["closing_date"].notna()
    &
    cleaned_jobs["closing_date"].isna(),
    "closing_date"
]

print(
    "\nRemaining invalid closing dates:"
)

print(
    bad_closing_dates
    .value_counts()
    .head(50)
)


# ============================================================
# 11. DATE FEATURES / TRANSFORMATION
# ============================================================

print("\n" + "=" * 70)
print("10. DATE FEATURES / TRANSFORMATION")
print("=" * 70)


# Year
cleaned_jobs["job_posted_year"] = (
    cleaned_jobs["date_posted"].dt.year
)


# Month number
cleaned_jobs["job_posted_month"] = (
    cleaned_jobs["date_posted"].dt.month
)


# Month name
cleaned_jobs["job_posted_month_name"] = (
    cleaned_jobs["date_posted"].dt.month_name()
)


# Day of month
cleaned_jobs["job_posted_day"] = (
    cleaned_jobs["date_posted"].dt.day
)


# Weekday name
cleaned_jobs["job_posted_weekday"] = (
    cleaned_jobs["date_posted"].dt.day_name()
)


# Quarter
cleaned_jobs["job_posted_quarter"] = (
    cleaned_jobs["date_posted"].dt.quarter
)


print(
    "Date features created:"
)

print(
    [
        "job_posted_year",
        "job_posted_month",
        "job_posted_month_name",
        "job_posted_day",
        "job_posted_weekday",
        "job_posted_quarter",
    ]
)


# ------------------------------------------------------------
# Verify date transformation
# ------------------------------------------------------------

valid_date_sample = cleaned_jobs.loc[
    cleaned_jobs["date_posted"].notna(),
    [
        "date_posted",
        "job_posted_year",
        "job_posted_month",
        "job_posted_month_name",
        "job_posted_day",
        "job_posted_weekday",
        "job_posted_quarter",
    ]
].head(10)

print(
    "\nSample transformed dates:"
)

print(
    valid_date_sample.to_string(index=False)
)


# ============================================================
# 12. SALARY RATE UNIT CLEANING
# ============================================================

print("\n" + "=" * 70)
print("11. SALARY RATE UNIT CLEANING")
print("=" * 70)

rate_unit_mapping = {

    # Hour
    "hour": "hour",
    "Hourly": "hour",
    "hourly": "hour",
    "Hour": "hour",
    "HOUR": "hour",
    "Hr": "hour",

    # Year
    "year": "year",
    "YEAR": "year",
    "yearly": "year",
    "Year": "year",
    "Annual": "year",
    "annual": "year",
    "Yr": "year",
    "yr": "year",
    "annually": "year",
    "Annum": "year",
    "p.a.": "year",
    "ANNUAL": "year",
    "Yearly": "year",
    "per annum": "year",
    "Annuelle": "year",

    # Month
    "month": "month",
    "MONTH": "month",
    "Monthly": "month",
    "monthly": "month",
    "Month": "month",

    # Week
    "week": "week",
    "weekly": "week",
    "Weekly": "week",
    "WEEK": "week",

    # Day
    "day": "day",
    "Daily": "day",
    "daily": "day",

    # Other legitimate units
    "session": "session",
    "per session": "session",
    "visit": "visit",
    "per visit": "visit",
    "shift": "shift",
    "mile": "mile",
    "one-time": "one-time",
    "Stipend": "stipend",
    "stipend": "stipend",
}

cleaned_jobs["salary_rate_unit"] = (
    cleaned_jobs["salary_rate_unit"]
    .replace(rate_unit_mapping)
)

print(
    cleaned_jobs["salary_rate_unit"]
    .value_counts(dropna=False)
)


# ============================================================
# 13. SALARY NUMERIC VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("12. SALARY NUMERIC VALIDATION")
print("=" * 70)

cleaned_jobs["salary_min"] = pd.to_numeric(
    cleaned_jobs["salary_min"],
    errors="coerce"
)

cleaned_jobs["salary_max"] = pd.to_numeric(
    cleaned_jobs["salary_max"],
    errors="coerce"
)


# ------------------------------------------------------------
# Negative salaries are invalid
# ------------------------------------------------------------

negative_min = (
    cleaned_jobs["salary_min"] < 0
)

negative_max = (
    cleaned_jobs["salary_max"] < 0
)

cleaned_jobs.loc[
    negative_min,
    "salary_min"
] = np.nan

cleaned_jobs.loc[
    negative_max,
    "salary_max"
] = np.nan


# ------------------------------------------------------------
# Zero salary
# ------------------------------------------------------------

cleaned_jobs.loc[
    cleaned_jobs["salary_min"] == 0,
    "salary_min"
] = np.nan

cleaned_jobs.loc[
    cleaned_jobs["salary_max"] == 0,
    "salary_max"
] = np.nan


print(
    "Invalid negative salary_min values:",
    negative_min.sum()
)

print(
    "Invalid negative salary_max values:",
    negative_max.sum()
)


# ============================================================
# 14. SALARY RANGE VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("13. SALARY RANGE VALIDATION")
print("=" * 70)

invalid_salary_range = (
    cleaned_jobs["salary_min"].notna()
    &
    cleaned_jobs["salary_max"].notna()
    &
    (
        cleaned_jobs["salary_min"]
        >
        cleaned_jobs["salary_max"]
    )
)

print(
    "Invalid salary ranges:",
    invalid_salary_range.sum()
)


# Do not swap min/max automatically.
# If the range is inconsistent, both are marked missing.

cleaned_jobs.loc[
    invalid_salary_range,
    [
        "salary_min",
        "salary_max"
    ]
] = np.nan


# ============================================================
# 15. SALARY MIDPOINT
# ============================================================

print("\n" + "=" * 70)
print("14. SALARY MIDPOINT")
print("=" * 70)

cleaned_jobs["salary_mid"] = np.where(

    cleaned_jobs["salary_min"].notna()
    &
    cleaned_jobs["salary_max"].notna(),

    (
        cleaned_jobs["salary_min"]
        +
        cleaned_jobs["salary_max"]
    ) / 2,

    np.nan
)

print(
    cleaned_jobs["salary_mid"]
    .describe()
)


# ============================================================
# 16. SALARY CURRENCY CLEANING
# ============================================================

print("\n" + "=" * 70)
print("15. SALARY CURRENCY CLEANING")
print("=" * 70)

cleaned_jobs["salary_currency"] = (
    cleaned_jobs["salary_currency"]
    .astype("string")
    .str.strip()
    .str.upper()
)

cleaned_jobs["salary_currency"] = (
    cleaned_jobs["salary_currency"]
    .replace(
        {
            "": pd.NA,
            "NONE": pd.NA,
            "N/A": pd.NA,
            "NA": pd.NA,
            "KČ": pd.NA,
        }
    )
)

print(
    cleaned_jobs["salary_currency"]
    .value_counts(dropna=False)
    .head(50)
)


# ============================================================
# 17. SALARY TYPE INSPECTION
# ============================================================

print("\n" + "=" * 70)
print("16. SALARY TYPE INSPECTION")
print("=" * 70)

print(
    cleaned_jobs["salary_type"]
    .value_counts(dropna=False)
    .head(50)
)

# We do NOT aggressively clean salary_type.
#
# Earlier inspection showed that this field contains
# contaminated values that appear to belong to other columns.
#
# Therefore we preserve the original information instead
# of making unsupported assumptions.


# ============================================================
# 18. PAY FREQUENCY INSPECTION
# ============================================================

print("\n" + "=" * 70)
print("17. PAY FREQUENCY INSPECTION")
print("=" * 70)

print(
    cleaned_jobs["pay_frequency"]
    .value_counts(dropna=False)
    .head(50)
)


# ============================================================
# 19. BONUS INSPECTION
# ============================================================

print("\n" + "=" * 70)
print("18. BONUS INSPECTION")
print("=" * 70)

print(
    cleaned_jobs["bonus"]
    .value_counts(dropna=False)
    .head(50)
)


# ============================================================
# 20. EQUITY INSPECTION
# ============================================================

print("\n" + "=" * 70)
print("19. EQUITY INSPECTION")
print("=" * 70)

print(
    cleaned_jobs["equity"]
    .value_counts(dropna=False)
    .head(50)
)


# ============================================================
# 21. ON TARGET EARNINGS INSPECTION
# ============================================================

print("\n" + "=" * 70)
print("20. ON TARGET EARNINGS INSPECTION")
print("=" * 70)

print(
    cleaned_jobs["on_target_earnings"]
    .value_counts(dropna=False)
    .head(50)
)


# ============================================================
# 22. LOCATION CLEANING
# ============================================================

print("\n" + "=" * 70)
print("21. LOCATION CLEANING")
print("=" * 70)

location_columns = [

    "city",
    "country",
    "location_resolved",
    "locations",
    "remote_eligibility_regions",

]

for column in location_columns:

    if column in cleaned_jobs.columns:

        cleaned_jobs[column] = (
            cleaned_jobs[column]
            .astype("string")
            .str.strip()
        )

        cleaned_jobs[column] = (
            cleaned_jobs[column]
            .replace(
                "",
                pd.NA
            )
        )

print(
    "Location fields cleaned."
)


# ============================================================
# 23. LATITUDE / LONGITUDE VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("22. COORDINATE VALIDATION")
print("=" * 70)

cleaned_jobs["latitude"] = pd.to_numeric(
    cleaned_jobs["latitude"],
    errors="coerce"
)

cleaned_jobs["longitude"] = pd.to_numeric(
    cleaned_jobs["longitude"],
    errors="coerce"
)


# Latitude must be between -90 and +90

invalid_latitude = (
    cleaned_jobs["latitude"].notna()
    &
    (
        (cleaned_jobs["latitude"] < -90)
        |
        (cleaned_jobs["latitude"] > 90)
    )
)


# Longitude must be between -180 and +180

invalid_longitude = (
    cleaned_jobs["longitude"].notna()
    &
    (
        (cleaned_jobs["longitude"] < -180)
        |
        (cleaned_jobs["longitude"] > 180)
    )
)


cleaned_jobs.loc[
    invalid_latitude,
    "latitude"
] = np.nan

cleaned_jobs.loc[
    invalid_longitude,
    "longitude"
] = np.nan

print(
    "Invalid latitude values:",
    invalid_latitude.sum()
)

print(
    "Invalid longitude values:",
    invalid_longitude.sum()
)


# ============================================================
# 24. EXPERIENCE LEVEL
# ============================================================

print("\n" + "=" * 70)
print("23. EXPERIENCE LEVEL")
print("=" * 70)

cleaned_jobs["experience_level"] = (
    cleaned_jobs["experience_level"]
    .astype("string")
    .str.strip()
)

cleaned_jobs["experience_level"] = (
    cleaned_jobs["experience_level"]
    .replace(
        "",
        pd.NA
    )
)

print(
    cleaned_jobs["experience_level"]
    .value_counts(
        dropna=False
    )
    .head(50)
)


# ============================================================
# 25. JOB LEVEL
# ============================================================

print("\n" + "=" * 70)
print("24. JOB LEVEL")
print("=" * 70)

cleaned_jobs["job_level_normalized"] = (
    cleaned_jobs["job_level_normalized"]
    .astype("string")
    .str.strip()
)

cleaned_jobs["job_level_normalized"] = (
    cleaned_jobs["job_level_normalized"]
    .replace(
        "",
        pd.NA
    )
)

print(
    cleaned_jobs["job_level_normalized"]
    .value_counts(
        dropna=False
    )
    .head(50)
)


# ============================================================
# 26. YEARS OF EXPERIENCE
# ============================================================

print("\n" + "=" * 70)
print("25. YEARS OF EXPERIENCE")
print("=" * 70)

cleaned_jobs["years_experience_numeric"] = pd.to_numeric(
    cleaned_jobs["years_experience_numeric"],
    errors="coerce"
)

negative_experience = (
    cleaned_jobs["years_experience_numeric"] < 0
)

cleaned_jobs.loc[
    negative_experience,
    "years_experience_numeric"
] = np.nan

print(
    cleaned_jobs["years_experience_numeric"]
    .describe()
)


# ============================================================
# 27. EDUCATION LEVEL
# ============================================================

print("\n" + "=" * 70)
print("26. EDUCATION LEVEL")
print("=" * 70)

cleaned_jobs["education_level"] = (
    cleaned_jobs["education_level"]
    .astype("string")
    .str.strip()
)

cleaned_jobs["education_level"] = (
    cleaned_jobs["education_level"]
    .replace(
        "",
        pd.NA
    )
)

print(
    cleaned_jobs["education_level"]
    .value_counts(
        dropna=False
    )
    .head(50)
)


# ============================================================
# 28. TEXT FIELD CLEANING
# ============================================================

print("\n" + "=" * 70)
print("27. TEXT FIELD CLEANING")
print("=" * 70)

text_columns = [

    "skills_required",
    "minimum_qualifications",
    "preferred_qualifications",
    "responsibilities",
    "certifications",
    "languages_required",
    "benefits",
    "job_description",

]

for column in text_columns:

    if column in cleaned_jobs.columns:

        cleaned_jobs[column] = (
            cleaned_jobs[column]
            .astype("string")
            .str.strip()
        )

        cleaned_jobs[column] = (
            cleaned_jobs[column]
            .replace(
                "",
                pd.NA
            )
        )

print(
    "Text fields processed:",
    len(
        [
            column
            for column in text_columns
            if column in cleaned_jobs.columns
        ]
    )
)


# ============================================================
# 29. NORMALIZE BOOLEAN-LIKE VALUES
# ============================================================

print("\n" + "=" * 70)
print("28. NORMALIZE BOOLEAN-LIKE VALUES")
print("=" * 70)


def normalize_boolean_column(series):
    """
    Convert clearly identifiable boolean values into
    pandas nullable boolean values.

    True / Yes / Y / 1  -> True
    False / No / N / 0  -> False
    Unknown values       -> <NA>
    Missing information remains missing.
    """

    normalized = (
        series
        .astype("string")
        .str.strip()
        .str.lower()
    )

    true_values = {
        "true",
        "yes",
        "y",
        "1",
    }

    false_values = {
        "false",
        "no",
        "n",
        "0",
    }

    result = pd.Series(
        pd.NA,
        index=series.index,
        dtype="boolean"
    )

    result.loc[
        normalized.isin(true_values)
    ] = True

    result.loc[
        normalized.isin(false_values)
    ] = False

    return result


boolean_like_columns = [

    "visa_sponsorship_available",
    "security_clearance",
    "relocation_assistance",
    "travel_required",

]


for column in boolean_like_columns:

    if column in cleaned_jobs.columns:

        print(
            f"\n--- {column} ---"
        )

        print(
            "Before:",
            cleaned_jobs[column].dtype
        )

        print(
            cleaned_jobs[column]
            .value_counts(
                dropna=False
            )
            .head(20)
        )

        cleaned_jobs[column] = (
            normalize_boolean_column(
                cleaned_jobs[column]
            )
        )

        print(
            "After:",
            cleaned_jobs[column].dtype
        )

        print(
            cleaned_jobs[column]
            .value_counts(
                dropna=False
            )
            .head(20)
        )


# ============================================================
# 30. TRAVEL PERCENTAGE
# ============================================================

print("\n" + "=" * 70)
print("29. TRAVEL PERCENTAGE")
print("=" * 70)

cleaned_jobs["travel_percentage"] = pd.to_numeric(
    cleaned_jobs["travel_percentage"],
    errors="coerce"
)

invalid_travel = (
    cleaned_jobs["travel_percentage"].notna()
    &
    (
        (cleaned_jobs["travel_percentage"] < 0)
        |
        (cleaned_jobs["travel_percentage"] > 100)
    )
)

cleaned_jobs.loc[
    invalid_travel,
    "travel_percentage"
] = np.nan

print(
    "Invalid travel percentages:",
    invalid_travel.sum()
)


# ============================================================
# 31. ANALYTICS FLAGS
# ============================================================

print("\n" + "=" * 70)
print("30. ANALYTICS FLAGS")
print("=" * 70)


# ------------------------------------------------------------
# Salary availability
# ------------------------------------------------------------

cleaned_jobs["has_salary"] = (
    cleaned_jobs["salary_min"].notna()
    |
    cleaned_jobs["salary_max"].notna()
)


# ------------------------------------------------------------
# Work model flags
# ------------------------------------------------------------

cleaned_jobs["is_remote"] = (
    cleaned_jobs["work_model"]
    .eq("Remote")
)

cleaned_jobs["is_hybrid"] = (
    cleaned_jobs["work_model"]
    .eq("Hybrid")
)

cleaned_jobs["is_onsite"] = (
    cleaned_jobs["work_model"]
    .eq("On-site")
)


# ------------------------------------------------------------
# Experience requirement availability
# ------------------------------------------------------------

cleaned_jobs["has_experience_requirement"] = (
    cleaned_jobs["years_experience_numeric"].notna()
    |
    cleaned_jobs["experience_level"].notna()
)


print(
    "Analytics flags created:"
)

print(
    [
        "has_salary",
        "is_remote",
        "is_hybrid",
        "is_onsite",
        "has_experience_requirement",
    ]
)


# ============================================================
# 32. DUPLICATE CHECK
# ============================================================

print("\n" + "=" * 70)
print("31. DUPLICATE CHECK")
print("=" * 70)

duplicate_count = (
    cleaned_jobs
    .duplicated()
    .sum()
)

print(
    "Exact duplicate rows:",
    duplicate_count
)

# IMPORTANT:
#
# We do not automatically delete duplicates.
#
# Identical job postings may legitimately occur
# across different sources or locations.


# ============================================================
# 33. POSSIBLE DUPLICATE JOB CHECK
# ============================================================

print("\n" + "=" * 70)
print("32. POSSIBLE DUPLICATE JOBS")
print("=" * 70)

duplicate_subset = [

    column
    for column in [
        "title",
        "company_name",
        "city",
        "country",
    ]
    if column in cleaned_jobs.columns

]

if duplicate_subset:

    possible_duplicates = (
        cleaned_jobs
        .duplicated(
            subset=duplicate_subset,
            keep=False
        )
        .sum()
    )

    print(
        "Duplicate check columns:",
        duplicate_subset
    )

    print(
        "Possible duplicate rows:",
        possible_duplicates
    )


# ============================================================
# 34. DATE LOGIC VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("33. DATE LOGIC VALIDATION")
print("=" * 70)

date_logic_error = (
    cleaned_jobs["date_posted"].notna()
    &
    cleaned_jobs["closing_date"].notna()
    &
    (
        cleaned_jobs["closing_date"]
        <
        cleaned_jobs["date_posted"]
    )
)

print(
    "Closing date before posting date:",
    date_logic_error.sum()
)

# We do not automatically modify these records.
# They should be investigated separately if necessary.


# ============================================================
# 35. FINAL SALARY SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("34. FINAL SALARY SUMMARY")
print("=" * 70)

print(
    "\nSalary minimum:"
)

print(
    cleaned_jobs["salary_min"]
    .describe()
)

print(
    "\nSalary maximum:"
)

print(
    cleaned_jobs["salary_max"]
    .describe()
)

print(
    "\nSalary midpoint:"
)

print(
    cleaned_jobs["salary_mid"]
    .describe()
)


# ============================================================
# 36. DATE FEATURE SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("35. DATE FEATURE SUMMARY")
print("=" * 70)

print(
    "\nJobs by posted year:"
)

print(
    cleaned_jobs["job_posted_year"]
    .value_counts(dropna=False)
    .sort_index()
)

print(
    "\nJobs by posted month:"
)

print(
    cleaned_jobs["job_posted_month"]
    .value_counts(dropna=False)
    .sort_index()
)


# ============================================================
# 37. FINAL MISSING VALUE REPORT
# ============================================================

print("\n" + "=" * 70)
print("36. FINAL MISSING VALUE REPORT")
print("=" * 70)

missing_report = (
    cleaned_jobs
    .isna()
    .sum()
    .sort_values(
        ascending=False
    )
)

missing_percentage = (
    cleaned_jobs
    .isna()
    .mean()
    .mul(100)
    .sort_values(
        ascending=False
    )
)

missing_report_df = pd.DataFrame(
    {
        "missing_count":
            missing_report,

        "missing_percentage":
            missing_percentage,
    }
)

print(
    missing_report_df
    .to_string()
)


# ============================================================
# 38. FINAL DATA TYPES
# ============================================================

print("\n" + "=" * 70)
print("37. FINAL DATA TYPES")
print("=" * 70)

print(
    cleaned_jobs.dtypes
)


# ============================================================
# 39. FINAL SHAPE
# ============================================================

print("\n" + "=" * 70)
print("38. FINAL SHAPE")
print("=" * 70)

print(
    "Raw shape:",
    jobs.shape
)

print(
    "Cleaned shape:",
    cleaned_jobs.shape
)


# ============================================================
# 40. ROW COUNT VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("39. ROW COUNT VALIDATION")
print("=" * 70)

if len(jobs) == len(cleaned_jobs):

    print(
        "PASS: No rows were removed."
    )

else:

    print(
        "WARNING: Row count changed."
    )


# ============================================================
# 41. PREPARE DATA FOR PARQUET
# ============================================================

print("\n" + "=" * 70)
print("40. PREPARING DATA FOR PARQUET")
print("=" * 70)

print(
    "Checking remaining object columns..."
)

remaining_object_columns = (
    cleaned_jobs
    .select_dtypes(
        include=["object"]
    )
    .columns
)

print(
    "Remaining object columns:",
    len(remaining_object_columns)
)

print(
    list(remaining_object_columns)
)


# ============================================================
# 42. SAVE CLEANED PARQUET
# ============================================================

print("\n" + "=" * 70)
print("41. SAVING CLEANED PARQUET")
print("=" * 70)

cleaned_jobs.to_parquet(
    PROCESSED_FILE,
    engine="pyarrow",
    index=False
)

print(
    "Saved:",
    PROCESSED_FILE
)


# ============================================================
# 43. SAVE CLEANED CSV
# ============================================================

print("\n" + "=" * 70)
print("42. SAVING CLEANED CSV")
print("=" * 70)

cleaned_jobs.to_csv(
    CSV_FILE,
    index=False
)

print(
    "Saved:",
    CSV_FILE
)


# ============================================================
# 44. RELOAD PROCESSED PARQUET
# ============================================================

print("\n" + "=" * 70)
print("43. VERIFY SAVED PARQUET")
print("=" * 70)

verification_jobs = pd.read_parquet(
    PROCESSED_FILE,
    engine="pyarrow"
)

print(
    "Reloaded shape:",
    verification_jobs.shape
)

print(
    "Original cleaned shape:",
    cleaned_jobs.shape
)


# ============================================================
# 45. VERIFY SAVED DATA
# ============================================================

print("\n" + "=" * 70)
print("44. VERIFY SAVED DATA")
print("=" * 70)

if verification_jobs.shape == cleaned_jobs.shape:

    print(
        "PASS: Row and column counts match."
    )

else:

    print(
        "WARNING: Saved file shape differs."
    )


# ============================================================
# 46. VERIFY IMPORTANT COLUMNS
# ============================================================

print("\n" + "=" * 70)
print("45. VERIFY IMPORTANT COLUMNS")
print("=" * 70)

required_columns = [

    "title",
    "company_name",
    "employment_type",
    "work_model",

    "salary_min",
    "salary_max",
    "salary_mid",
    "salary_currency",
    "salary_rate_unit",

    "date_posted",
    "closing_date",

    "job_posted_year",
    "job_posted_month",
    "job_posted_month_name",
    "job_posted_day",
    "job_posted_weekday",
    "job_posted_quarter",

    "city",
    "country",

    "has_salary",
    "is_remote",
    "is_hybrid",
    "is_onsite",
    "has_experience_requirement",

]

missing_columns = [

    column
    for column in required_columns
    if column not in verification_jobs.columns

]

if not missing_columns:

    print(
        "PASS: All important columns exist."
    )

else:

    print(
        "WARNING: Missing columns:"
    )

    print(
        missing_columns
    )


# ============================================================
# 47. VERIFY DATE COLUMNS
# ============================================================

print("\n" + "=" * 70)
print("46. VERIFY DATE COLUMNS")
print("=" * 70)

print(
    "date_posted dtype:",
    verification_jobs["date_posted"].dtype
)

print(
    "closing_date dtype:",
    verification_jobs["closing_date"].dtype
)

print(
    "job_posted_year dtype:",
    verification_jobs["job_posted_year"].dtype
)

print(
    "job_posted_month dtype:",
    verification_jobs["job_posted_month"].dtype
)


# ============================================================
# 48. VERIFY SALARY COLUMNS
# ============================================================

print("\n" + "=" * 70)
print("47. VERIFY SALARY COLUMNS")
print("=" * 70)

print(
    "salary_min dtype:",
    verification_jobs["salary_min"].dtype
)

print(
    "salary_max dtype:",
    verification_jobs["salary_max"].dtype
)

print(
    "salary_mid dtype:",
    verification_jobs["salary_mid"].dtype
)


# ============================================================
# 49. VERIFY BOOLEAN COLUMNS
# ============================================================

print("\n" + "=" * 70)
print("48. VERIFY BOOLEAN COLUMNS")
print("=" * 70)

for column in boolean_like_columns:

    if column in verification_jobs.columns:

        print(
            f"{column}:",
            verification_jobs[column].dtype
        )


print(
    "\nhas_salary:",
    verification_jobs["has_salary"].dtype
)

print(
    "is_remote:",
    verification_jobs["is_remote"].dtype
)

print(
    "is_hybrid:",
    verification_jobs["is_hybrid"].dtype
)

print(
    "is_onsite:",
    verification_jobs["is_onsite"].dtype
)


# ============================================================
# 50. FINAL TRANSFORMED SAMPLE
# ============================================================

print("\n" + "=" * 70)
print("49. FINAL TRANSFORMED SAMPLE")
print("=" * 70)

sample_columns = [

    "title",
    "company_name",
    "country",
    "work_model",
    "employment_type",

    "date_posted",
    "job_posted_year",
    "job_posted_month",
    "job_posted_month_name",

    "salary_min",
    "salary_max",
    "salary_mid",
    "salary_currency",
    "salary_rate_unit",

    "has_salary",
    "is_remote",
    "is_hybrid",
    "is_onsite",

]

sample_columns = [
    column
    for column in sample_columns
    if column in verification_jobs.columns
]

print(
    verification_jobs[
        sample_columns
    ]
    .head(10)
    .to_string(index=False)
)


# ============================================================
# 51. FINAL ETL STATUS
# ============================================================

print("\n" + "=" * 70)
print("50. FINAL ETL STATUS")
print("=" * 70)

print(
    "Raw data loaded              : YES"
)

print(
    "Raw data preserved           : YES"
)

print(
    "General text cleaned        : YES"
)

print(
    "Work model cleaned           : YES"
)

print(
    "Employment type cleaned      : YES"
)

print(
    "Title quality checked        : YES"
)

print(
    "Date posted processed        : YES"
)

print(
    "Closing date processed       : YES"
)

print(
    "Date features created        : YES"
)

print(
    "Salary units standardized    : YES"
)

print(
    "Salary numeric validation    : YES"
)

print(
    "Salary midpoint created      : YES"
)

print(
    "Currency standardized        : YES"
)

print(
    "Location fields cleaned      : YES"
)

print(
    "Coordinates validated        : YES"
)

print(
    "Experience checked           : YES"
)

print(
    "Education checked            : YES"
)

print(
    "Text fields cleaned          : YES"
)

print(
    "Boolean fields normalized    : YES"
)

print(
    "Travel percentage validated  : YES"
)

print(
    "Analytics flags created      : YES"
)

print(
    "Duplicate check completed    : YES"
)

print(
    "Date logic checked           : YES"
)

print(
    "Missing-value report created : YES"
)

print(
    "Processed Parquet saved      : YES"
)

print(
    "Processed CSV saved          : YES"
)

print(
    "Saved Parquet verified       : YES"
)


# ============================================================
# 52. FINAL OUTPUT
# ============================================================

print("\n" + "=" * 70)
print("ETL + TRANSFORMATION COMPLETE")
print("=" * 70)

print(
    "\nProcessed Parquet:",
    PROCESSED_FILE
)

print(
    "Processed CSV:",
    CSV_FILE
)

print(
    "Final shape:",
    cleaned_jobs.shape
)

print(
    "\nRaw dataset remains untouched."
)

print(
    "Cleaned + transformed dataset is ready for the next stage."
)

print("\n" + "=" * 70)
print("PIPELINE FINISHED")
print("=" * 70)