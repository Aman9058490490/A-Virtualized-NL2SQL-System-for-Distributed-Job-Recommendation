import pandas as pd
from innovation1 import auto_merge_dataframes


def test_auto_merge_simple():
    df_course = pd.DataFrame([{'se_Job_Id': 'SE1', 'se_Role': 'Software Development'}])
    df_job = pd.DataFrame([{'fe_Job_Id': 'FE1', 'fe_Role': 'Frontend Development'}])
    merged = auto_merge_dataframes(df_course, df_job)
    assert not merged.empty
    # Expect Role column after normalization
    assert any(col.lower() == 'role' for col in merged.columns) or any('Role' in col for col in merged.columns)
