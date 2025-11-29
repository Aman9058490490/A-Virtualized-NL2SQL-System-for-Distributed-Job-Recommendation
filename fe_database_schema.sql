-- Create table for fe_database
CREATE TABLE IF NOT EXISTS fe_jobs (
    fe_Job_Id VARCHAR(50) PRIMARY KEY,
    fe_Experience VARCHAR(100),
    fe_Qualifications TEXT,
    fe_Salary_Range VARCHAR(100),
    fe_location VARCHAR(100),
    fe_Country VARCHAR(100),
    fe_Work_Type VARCHAR(50),
    fe_Company_Size VARCHAR(50),
    fe_Preference TEXT,
    fe_Contact_Person VARCHAR(100),
    fe_Job_Title VARCHAR(200),
    fe_Role VARCHAR(100),
    fe_Job_Description TEXT,
    fe_Benefits TEXT,
    fe_skills TEXT,
    fe_Responsibilities TEXT,
    fe_Company VARCHAR(100),
    fe_Company_Profile TEXT
);