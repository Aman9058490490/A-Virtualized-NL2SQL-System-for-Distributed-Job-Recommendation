import pandas as pd

from innovation1 import execute_etl_code


def _make_course_df():
    return pd.DataFrame(
        [
            {"se_Job_Id": "SE1", "se_Job_Title": "Backend Developer", "se_Experience": "3 years"},
            {"se_Job_Id": "SE2", "se_Job_Title": "Cloud Engineer", "se_Experience": "5 years"},
        ]
    )


def _make_job_df():
    return pd.DataFrame(
        [
            {"fe_Job_Id": "FE1", "fe_Job_Title": "Frontend Developer", "fe_Experience": "2 years"},
            {"fe_Job_Id": "FE2", "fe_Job_Title": "UI Developer", "fe_Experience": "4 years"},
        ]
    )


def test_execute_etl_code_success():
    course_df = _make_course_df()
    job_df = _make_job_df()

    etl_code = """
import pandas as pd
if isinstance(df_course, pd.DataFrame) and isinstance(df_job, pd.DataFrame):
    df_course2 = df_course.rename(columns=lambda c: c.replace('se_', ''))
    df_job2 = df_job.rename(columns=lambda c: c.replace('fe_', ''))
    df_merged = pd.concat([df_course2, df_job2], ignore_index=True, sort=True)
else:
    df_merged = pd.DataFrame()
"""

    merged = execute_etl_code(etl_code, course_df, job_df)
    assert not merged.empty
    assert merged.shape[0] == course_df.shape[0] + job_df.shape[0]
    # columns should have prefixes removed
    assert any(col in merged.columns for col in ["Job_Id", "Job_Title"])


def test_execute_etl_code_failure_fallback():
    course_df = _make_course_df()
    job_df = _make_job_df()

    # this ETL will raise; sandbox should catch and fallback to safe merge
    etl_code = "raise RuntimeError('boom')"

    merged = execute_etl_code(etl_code, course_df, job_df)
    assert not merged.empty
    assert merged.shape[0] == course_df.shape[0] + job_df.shape[0]
    # fallback strips prefixes
    assert any(col in merged.columns for col in ["Job_Id", "Job_Title"]) or any(col in merged.columns for col in ["se_Job_Id", "fe_Job_Id"]) 
