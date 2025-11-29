# Out-of-Scope Query Handling - Implementation Guide

## Overview
This document describes the improvements made to handle queries that fall outside the database scope (i.e., queries about data not available in the software engineering and frontend engineering job databases).

## Problem Statement
Previously, when users asked about topics not in the database (e.g., medical jobs, teaching positions, etc.), the system would simply return:
> "No matching results were found in either database."

This response was not helpful as it didn't guide users toward what they COULD ask about.

## Solution Implemented

### 1. Enhanced LLM Prompt in `query_analyzer.py`

#### Added Section: "HANDLING OUT-OF-SCOPE QUERIES"
The system prompt now instructs the first LLM to:
- Generate the best possible SQL queries even for out-of-scope requests
- In the `natural_query` field, clearly explain what information is NOT available
- Suggest 2-3 alternative queries that WOULD work with the available data
- Ask the second LLM to provide helpful suggestions

**Example Prompt Instruction:**
```
If the user's query asks about information NOT available in either database
(e.g., medical jobs, teaching positions, non-tech roles):

1. Generate the BEST POSSIBLE SQL queries that retrieve the most relevant data
2. In the "natural_query", CLEARLY explain:
   - What information is NOT available in the database
   - Suggest 2-3 similar queries that WOULD work with the available data
   - Ask the second LLM to acknowledge limitations and provide alternative suggestions
```

#### Enhanced NATURAL_QUERY RULES
Added guidance for the LLM to:
- Include queries about data not in the schema as things SQL cannot answer
- Instruct the second LLM to politely explain unavailable information
- Suggest alternative queries that would work
- Provide partial matches if any relevant data exists

### 2. Improved Empty Result Handling in `executor.py`

#### Updated `generate_final_answer()` Method
**Function Signature Changed:**
```python
# Before
def generate_final_answer(self, merged_df: pd.DataFrame, natural_query: str):

# After
def generate_final_answer(self, merged_df: pd.DataFrame, natural_query: str, original_user_query: str = ""):
```

#### When Results are Empty:
Instead of returning a generic message, the system now:

1. **Calls the LLM** with a specialized prompt that:
   - Explains what databases are available (Software + Frontend engineering jobs)
   - Asks for a polite explanation of why the query can't be answered
   - Requests 3 specific alternative query suggestions
   - Uses a friendly, helpful tone

**Example Prompt:**
```python
"The user asked: '{user_query}'

Our database contains ONLY:
- Software Engineering jobs (backend, full-stack, cloud, DevOps roles)
- Frontend Engineering jobs (React, Angular, Vue, UI/UX roles)

No matching results were found for this query.

Please:
1. Politely explain that the query is not available in our database
2. Suggest 3 relevant alternative queries that WOULD work with our database
3. Make suggestions based on what's actually available (software or frontend engineering jobs)

Format your response in a friendly, helpful manner."
```

#### When Results Exist but are Limited:
The improved prompt now:
- Acknowledges if the user asked about something outside the database scope
- Provides clear suggestions for better queries
- Uses the available data to give the best possible answer

**Enhanced Prompt:**
```python
"You are an expert job-market analyst.

DATABASE CONTAINS: Software engineering jobs and frontend engineering jobs ONLY.

DATASET:
{table_text}

TASK:
{natural_query}

Instructions:
- Answer the user's question using the dataset
- If the user asked about something NOT in our database scope, acknowledge this
  and suggest what they COULD ask about instead (software or frontend jobs)
- If dataset has limited results, mention that and provide suggestions
- Be conversational and helpful
- DO NOT mention SQL or technical database details
- Provide clear, actionable insights"
```

### 3. Backend Integration in `backend/app.py`

Updated both query endpoints to pass the original user query:

```python
# Single query endpoint
final_answer = db_executor.generate_final_answer(
    merged_df,
    decomposition.natural_query,
    nl_query  # <-- Original user query added
)

# Batch query endpoint
final_answer = db_executor.generate_final_answer(
    merged_df,
    decomposition.natural_query,
    query  # <-- Original user query added
)
```

## Example Scenarios

### Scenario 1: Completely Out-of-Scope Query
**User Query:** "Show me medical jobs for doctors"

**Expected Response:**
```
I understand you're looking for medical jobs for doctors. However, our database 
currently only contains information about software engineering and frontend 
engineering positions.

Here are some alternative queries you might find helpful:

1. "Show me software engineering jobs with 5+ years of experience"
2. "Find frontend developer positions requiring React skills"
3. "List remote full-stack developer jobs"

Would you like to explore any of these areas instead?
```

### Scenario 2: Partially Related Query
**User Query:** "Find teaching positions for programming instructors"

**Expected Response:**
```
Our database doesn't include teaching positions specifically. However, we do have 
software and frontend engineering jobs that might interest someone with programming 
expertise.

You might want to try:

1. "Show me senior software engineer positions"
2. "Find frontend jobs requiring JavaScript and mentorship skills"
3. "List software development roles with leadership opportunities"

These positions often involve mentoring and knowledge-sharing aspects that might 
align with your interests.
```

### Scenario 3: Limited Results
**User Query:** "Jobs for blockchain developers"

**Expected Response:**
```
Our database has limited information about blockchain-specific roles. However, 
here's what I found from our software engineering positions:

[Shows closest matches like full-stack or backend roles]

For better results, you might try:

1. "Software engineering jobs requiring distributed systems experience"
2. "Backend developer positions with cryptocurrency or fintech companies"
3. "Full-stack roles with blockchain-related skills"
```

## Technical Benefits

1. **Better User Experience**: Users receive helpful guidance instead of dead-end error messages
2. **Increased Engagement**: Alternative suggestions keep users engaged with the system
3. **Reduced Confusion**: Clear explanations of database limitations prevent frustration
4. **Learning Aid**: Suggestions teach users what types of queries work well

## Configuration

The LLM temperature settings for these responses:
- **Empty results prompt**: `temperature=0.3` (slightly creative for varied suggestions)
- **Regular analysis prompt**: `temperature=0.2` (balanced accuracy and readability)

## Testing Recommendations

Test with these out-of-scope queries:
1. "Find me teaching jobs"
2. "Show medical positions"
3. "List sales and marketing roles"
4. "Find jobs in the automotive industry"
5. "Show me legal positions for lawyers"

Each should return:
- Polite acknowledgment of limitations
- 2-3 relevant alternative suggestions
- Friendly, helpful tone
- No technical jargon (SQL, database mentions, etc.)

## Backup

The original `query_analyzer.py` has been backed up to `query_analyzer_backup.py` for reference.
