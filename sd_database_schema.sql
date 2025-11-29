-- Create table for sd_database
CREATE TABLE IF NOT EXISTS sd_jobs (
    sd_Job_Id VARCHAR(50) PRIMARY KEY,
    sd_Experience VARCHAR(100),
    sd_Qualifications TEXT,
    sd_Salary_Range VARCHAR(100),
    sd_location VARCHAR(100),
    sd_Country VARCHAR(100),
    sd_Work_Type VARCHAR(50),
    sd_Company_Size VARCHAR(50),
    sd_Preference TEXT,
    sd_Contact_Person VARCHAR(100),
    sd_Job_Title VARCHAR(200),
    sd_Role VARCHAR(100),
    sd_Job_Description TEXT,
    sd_Benefits TEXT,
    sd_skills TEXT,
    sd_Responsibilities TEXT,
    sd_Company VARCHAR(100),
    sd_Company_Profile TEXT
);