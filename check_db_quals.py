from utils import load_database_config
import pymysql

# Check software DB
cfg = load_database_config("COURSE_DB")
conn = pymysql.connect(host=cfg.host, port=cfg.port, user=cfg.user, password=cfg.password, database=cfg.database)
cur = conn.cursor()

print("=== Sample Qualifications from software_engineer_jobs ===")
cur.execute("SELECT se_Job_Id, se_Qualifications FROM software_engineer_jobs LIMIT 20")
for row in cur.fetchall():
    print(f"ID: {row[0]}, Qual: {row[1]}")

print("\n=== Count of rows with 'tech' in qualifications ===")
cur.execute("SELECT COUNT(*) FROM software_engineer_jobs WHERE LOWER(se_Qualifications) LIKE '%tech%'")
print(f"With 'tech': {cur.fetchone()[0]}")

print("\n=== Count with normalized 'btech' ===")
cur.execute("SELECT COUNT(*) FROM software_engineer_jobs WHERE LOWER(REPLACE(REPLACE(se_Qualifications, '.', ''), ' ', '')) LIKE '%btech%'")
print(f"With 'btech' normalized: {cur.fetchone()[0]}")

cur.close()
conn.close()

# Check frontend DB
cfg2 = load_database_config("JOB_DB")
conn2 = pymysql.connect(host=cfg2.host, port=cfg2.port, user=cfg2.user, password=cfg2.password, database=cfg2.database)
cur2 = conn2.cursor()

print("\n=== Sample Qualifications from frontend_engineer_jobs ===")
cur2.execute("SELECT fe_Job_Id, fe_Qualifications FROM frontend_engineer_jobs LIMIT 20")
for row in cur2.fetchall():
    print(f"ID: {row[0]}, Qual: {row[1]}")

cur2.close()
conn2.close()
