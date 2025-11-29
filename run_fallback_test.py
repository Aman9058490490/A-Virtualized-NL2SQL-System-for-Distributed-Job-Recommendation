from query_analyzer import QueryAnalyzer

# Use a Dummy client so we don't need a Groq API key
class DummyClient:
    pass

qa = QueryAnalyzer(DummyClient())
res = qa._fallback_decomposition('list all whose qualification is B.Tech')
print('COURSE_SQL:\n', res.course_sql)
print('\nJOB_SQL:\n', res.job_sql)
