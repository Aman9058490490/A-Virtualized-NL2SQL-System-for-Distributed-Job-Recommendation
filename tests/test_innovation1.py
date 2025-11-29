import pandas as pd
from innovation1 import auto_merge_dataframes


def make_course_df():
    data = {
        'se_Job_Id': ['SE1'],
        'se_Job_Title': ['Backend Developer'],
        'se_Role': ['Software Development'],
        'se_skills': ['Python, SQL'],
        'se_Qualifications': ['MTech']
    }
    return pd.DataFrame(data)


def make_job_df():
    data = {
        'fe_Job_Id': ['FE1'],
        'fe_Job_Title': ['React Developer'],
        'fe_Role': ['Frontend Development'],
        'fe_skills': ['React, TypeScript'],
        'fe_Qualifications': ['BTech']
    }
    return pd.DataFrame(data)


def test_auto_merge_basic():
    df_course = make_course_df()
    df_job = make_job_df()
    merged = auto_merge_dataframes(df_course, df_job)
    # merged should be a DataFrame containing rows from both
    assert not merged.empty
    # after normalization merged should have Role column (without prefixes)
    assert 'Role' in merged.columns or any(c.endswith('_Role') for c in merged.columns)
    # there should be at least two rows combined
    assert len(merged) >= 2
