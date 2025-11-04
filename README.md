# annalyticai

Turn messy job postings into clean, structured, analytics-ready data. 
The system fetches jobs from RapidAPI, deduplicates and normalizes them, then uses an LLM (guided by your curated QUAL rules and title heuristics) to parse each description into a canonical title, skills/stack, and a short summary. 
Parsed results are merged incrementally into a unified feature dataset for search, matching, and market analytics.


```mermaid
graph TD
A[Rapid API] --> B[RapidTransformer\ndedup, normalize]
B --> C[Jobs DF\nkey: job_description_id, job_id]
C --> D[Jobs Description DF\nkey: job_description_id]
D --> E[JobParser]
E --> F[OpenAI Client]
F --> G[Parsed DF incremental\nkey: job_description_id]
C --> H[JobTransformer\nmerge/upsert]
G --> H
H --> I[Feature DF\nexport JSON/Parquet]
```
