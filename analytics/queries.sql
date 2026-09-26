-- ============================================================
-- 1. JOB POSTINGS BY COUNTRY
-- ============================================================

SELECT
    country,
    COUNT(*) AS job_count
FROM jobs
WHERE country IS NOT NULL
  AND TRIM(country) <> ''
GROUP BY country
ORDER BY job_count DESC
LIMIT 20;

-- ============================================================
-- 2. MOST COMMON JOB TITLES
-- ============================================================

SELECT
    normalized_title,
    COUNT(*) AS job_count
FROM jobs
WHERE normalized_title IS NOT NULL
  AND TRIM(normalized_title) <> ''
GROUP BY normalized_title
ORDER BY job_count DESC
LIMIT 20;

-- ============================================================
-- 3. JOB POSTINGS BY WORK MODEL
-- ============================================================

SELECT
    work_model,
    COUNT(*) AS job_count
FROM jobs
WHERE work_model IS NOT NULL
  AND TRIM(work_model) <> ''
GROUP BY work_model
ORDER BY job_count DESC;

-- ============================================================
-- 4. JOB POSTINGS BY COUNTRY AND WORK MODEL
-- ============================================================

SELECT
    country,
    work_model,
    COUNT(*) AS job_count
FROM jobs
WHERE country IS NOT NULL
  AND TRIM(country) <> ''
  AND work_model IS NOT NULL
  AND TRIM(work_model) <> ''
  AND country IN (
      'United States',
      'United Kingdom',
      'Canada',
      'India',
      'France',
      'Australia',
      'Germany',
      'Mexico',
      'Netherlands',
      'Spain'
  )
GROUP BY
    country,
    work_model
ORDER BY
    country,
    job_count DESC;

-- ============================================================
-- 5. JOB POSTINGS BY CAREER LEVEL
-- ============================================================

SELECT
    job_level_normalized,
    COUNT(*) AS job_count
FROM jobs
WHERE job_level_normalized IS NOT NULL
  AND TRIM(job_level_normalized) <> ''
GROUP BY job_level_normalized
ORDER BY job_count DESC;

-- ============================================================
-- 6. MOST COMMON ENTRY-LEVEL JOB TITLES
-- ============================================================

SELECT
    normalized_title,
    COUNT(*) AS job_count
FROM jobs
WHERE job_level_normalized = 'Entry'
  AND normalized_title IS NOT NULL
  AND TRIM(normalized_title) <> ''
GROUP BY normalized_title
ORDER BY job_count DESC
LIMIT 20;

-- ============================================================
-- 7. SOFTWARE, DATA, BACKEND AND DEVOPS JOB TITLES
-- ============================================================

SELECT
    normalized_title,
    COUNT(*) AS job_count
FROM jobs
WHERE (
    normalized_title ILIKE '%python%'
    OR normalized_title ILIKE '%software%'
    OR normalized_title ILIKE '%backend%'
    OR normalized_title ILIKE '%data%'
    OR normalized_title ILIKE '%devops%'
)
GROUP BY normalized_title
ORDER BY job_count DESC
LIMIT 30;


-- ============================================================
-- 8. CAREER LEVELS IN SOFTWARE, DATA, BACKEND AND DEVOPS JOBS
-- ============================================================

SELECT
    job_level_normalized,
    COUNT(*) AS job_count
FROM jobs
WHERE (
    normalized_title ILIKE '%python%'
    OR normalized_title ILIKE '%software%'
    OR normalized_title ILIKE '%backend%'
    OR normalized_title ILIKE '%data%'
    OR normalized_title ILIKE '%devops%'
)
AND job_level_normalized IS NOT NULL
GROUP BY job_level_normalized
ORDER BY job_count DESC;

-- ============================================================
-- 9. ENTRY, JUNIOR AND INTERN TECHNICAL JOB TITLES
-- ============================================================

SELECT
    normalized_title,
    COUNT(*) AS job_count
FROM jobs
WHERE job_level_normalized IN ('Entry', 'Junior', 'Intern')
  AND (
      normalized_title ILIKE '%python%'
      OR normalized_title ILIKE '%software%'
      OR normalized_title ILIKE '%backend%'
      OR normalized_title ILIKE '%data%'
      OR normalized_title ILIKE '%devops%'
  )
GROUP BY normalized_title
ORDER BY job_count DESC
LIMIT 30;

-- ============================================================
-- 10. ENTRY-LEVEL TECHNICAL JOBS BY COUNTRY
-- ============================================================

SELECT
    country,
    COUNT(*) AS job_count
FROM jobs
WHERE job_level_normalized IN ('Entry', 'Junior', 'Intern')
  AND (
      normalized_title ILIKE '%python%'
      OR normalized_title ILIKE '%software%'
      OR normalized_title ILIKE '%backend%'
      OR normalized_title ILIKE '%devops%'
  )
  AND country IS NOT NULL
GROUP BY country
ORDER BY job_count DESC
LIMIT 20;

-- ============================================================
-- 12. JOB POSTINGS WITH AND WITHOUT SALARY INFORMATION
-- ============================================================
SELECT 
    has_salary,
    COUNT(*) AS job_count
FROM jobs
GROUP BY has_salary
ORDER BY job_count DESC;

-- ============================================================
-- 13. JOB POSTINGS WITH SALARY INFORMATION BY COUNTRY
-- ============================================================
SELECT 
    country,
    COUNT(*) AS job_count
FROM jobs
WHERE has_salary = TRUE
    AND country IS NOT NULL
    GROUP BY country
    ORDER BY job_count DESC
    LIMIT 20;

-- ============================================================
-- 14. SALARY REPORTING RATE BY COUNTRY
-- ============================================================

SELECT 
    country,
    COUNT(*) AS total_jobs,
    SUM(CASE WHEN has_salary = TRUE THEN 1 ELSE 0 END) AS jobs_with_salary,
    ROUND(
        SUM(CASE WHEN has_salary = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
        2
    ) AS salary_reporting_rate
FROM jobs
WHERE country IS NOT NULL
GROUP BY country
HAVING COUNT(*) >= 100
ORDER BY salary_reporting_rate DESC
LIMIT 20;

-- ============================================================
-- 15. AVERAGE SALARY BY CAREER LEVEL
-- ============================================================
-- Preliminary analysis only.
-- Salary values have different rate units (hour, year, month, etc.).
-- Averages across units are not directly comparable.
-- See Query #16 for salary averages grouped by unit.

SELECT
    job_level_normalized,
    AVG(salary_mid) AS average_salary,
    COUNT(salary_mid) AS salary_count
FROM jobs
WHERE job_level_normalized IS NOT NULL
  AND salary_mid IS NOT NULL
GROUP BY job_level_normalized
ORDER BY average_salary DESC;

