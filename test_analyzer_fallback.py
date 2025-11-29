from groq_client import GroqClient
from query_analyzer import QueryAnalyzer

# Use a dummy groq client that won't be called (we'll use fallback)
client = GroqClient(api_key='dummy', model='meta-llama/llama-4-scout-17b-16e-instruct')
qa = QueryAnalyzer(client)
res = qa._fallback_decomposition("List all students whose salary is greater then $56k-$85k and are Mobile App Developers")
print("COURSE_SQL:\n", res.course_sql)
print("\nJOB_SQL:\n", res.job_sql)
print("\nPROMPT:\n", res.unstructured_prompt)
