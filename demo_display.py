import pandas as pd
from run_demo import _print_dataframe, _select_course_columns, _select_job_columns, _select_merged_columns

# Construct sample CourseDB (sd_) dataframe with a few rows from user's paste
course_rows = [
    {
        "sd_Job_Id": 15900000000000,
        "sd_Experience": "3 to 13 Years",
        "sd_Qualifications": "MBA",
        "sd_Salary_Range": "$59K-$130K",
        "sd_location": "Macao",
        "sd_Country": "Macao SAR, China",
        "sd_Work_Type": "Full-Time",
        "sd_Company_Size": 54131,
        "sd_Preference": "Female",
        "sd_Contact_Person": "Kristine Taylor",
        "sd_Job_Title": "Software Developer",
        "sd_Role": "Mobile App Developer",
        "sd_Job_Description": "Mobile App Developers design and develop mobile applications for various platforms.",
        "sd_Benefits": "{'Employee Referral Programs', 'Financial Counseling'}",
        "sd_skills": "Mobile app development languages (e.g., Java, Swift, Kotlin); React Native; Flutter",
        "sd_Responsibilities": "Create mobile applications for iOS and Android platforms.",
        "sd_Company": "Massachusetts Mutual Life Insurance",
        "sd_Company_Profile": {"Sector":"Insurance","Industry":"Insurance: Life, Health (Mutual)","City":"Springfield"}
    },
    {
        "sd_Job_Id": 43300000000000,
        "sd_Experience": "4 to 13 Years",
        "sd_Qualifications": "B.Tech",
        "sd_Salary_Range": "$58K-$83K",
        "sd_location": "Algiers",
        "sd_Country": "Algeria",
        "sd_Work_Type": "Full-Time",
        "sd_Company_Size": 134290,
        "sd_Preference": "Female",
        "sd_Contact_Person": "Lisa Perkins",
        "sd_Job_Title": "Software Developer",
        "sd_Role": "Mobile App Developer",
        "sd_Job_Description": "Design and develop mobile applications.",
        "sd_Benefits": "{'Tuition Reimbursement', 'Stock Options'}",
        "sd_skills": "Java, Kotlin, React Native",
        "sd_Responsibilities": "Optimize mobile app performance.",
        "sd_Company": "Mohawk Industries",
        "sd_Company_Profile": {"Sector":"Flooring","City":"Calhoun"}
    }
]

job_rows = [
    {
        "fe_Job_Id": 50000000000000,
        "fe_Experience": "1 to 11 Years",
        "fe_Qualifications": "B.Tech",
        "fe_Salary_Range": "$55K-$87K",
        "fe_location": "Tashkent",
        "fe_Country": "Uzbekistan",
        "fe_Work_Type": "Full-Time",
        "fe_Company_Size": 133981,
        "fe_Preference": "Male",
        "fe_Contact_Person": "Paul Baker",
        "fe_Job_Title": "Software Developer",
        "fe_Role": "Mobile App Developer",
        "fe_Job_Description": "Mobile app development for cross-platform.",
        "fe_Benefits": "{'Life and Disability Insurance'}",
        "fe_skills": "Java; React Native; Flutter",
        "fe_Responsibilities": "Create mobile applications for iOS and Android.",
        "fe_Company": "Autoliv",
        "fe_Company_Profile": {"Sector":"Automotive","City":"Auburn Hills"}
    }
]

course_df = pd.DataFrame(course_rows)
job_df = pd.DataFrame(job_rows)

merged_df = pd.concat([job_df, course_df.rename(columns=lambda c: c.replace('sd_', 'fe_'))], sort=False, ignore_index=True)

print('\n=== Demo: CourseDB ===')
_print_dataframe('CourseDB results', _select_course_columns(course_df), max_rows=10, max_col_width=80)

print('\n=== Demo: JobDB ===')
_print_dataframe('JobDB results', _select_job_columns(job_df), max_rows=10, max_col_width=80)

print('\n=== Demo: Merged ===')
_print_dataframe('Merged results', _select_merged_columns(merged_df), max_rows=10, max_col_width=80)
