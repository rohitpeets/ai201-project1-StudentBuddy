# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
Domain : Mcneese State University Professor Reviews

Each student has a different method of learning that works for them.  while going through college every student is faced with a situation where they end up taking a class under a professor whose method of teaching is different from what works for that specific student. There is a need for students to have access to information about the way every professor teaches, their grading style, their exam patterns and other useful info. 
This system allows students to make queries in their natural language.
---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->
| #  | Source | Description | URL or location |
|----|--------|-------------|-----------------|
| 1  | Rate My Professors | Student reviews for Bei Xie (Computer Science)           | documents/Bei_Xie.txt           |
| 2  | Rate My Professors | Student reviews for Jennifer Lavergne (Computer Science) | documents/Jennifer_Lavergne.txt |
| 3  | Rate My Professors | Student reviews for Vipin Menon (Computer Science)       | documents/Vipin_Menon.txt       |
| 4  | Rate My Professors | Student reviews for Andrew Mudd (Biology)                | documents/Andrew_Mudd.txt       |
| 5  | Rate My Professors | Student reviews for Constance Kersten (Biology)          | documents/Constance_Kersten.txt |
| 6  | Rate My Professors | Student reviews for Susie Beasley (Biology)              | documents/Susie_Beasley.txt     |
| 7  | Rate My Professors | Student reviews for Tristan Salinas (Mathematics)        | documents/Tristan_Salinas.txt   |
| 8  | Rate My Professors | Student reviews for Lara Guidroz (Mathematics)           | documents/Lara_Guidroz.txt      |
| 9  | Rate My Professors | Student reviews for Shaikh Samad (Mathematics)           | documents/Shaikh_Samad.txt      |
| 10 | Rate My Professors | Student reviews for Lyle Hardee (Mathematics)            | documents/Lyle_Hardee.txt       |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

 Input Document Format

 Our input documents are structured review documents for professors at Mcneese State University. One Text file for each professor.
 Each file is split into two sections:

 First section: [A header Block] contains aggregate information including 
 -professor name
 -department
 -Overall Rating
 -Difficulty Score
 -A would take again percentage 
 -A brief summary
 Second section: [Individual review section]
 contains individual reviews by students each review being separated by a delimiter {----}.


**Chunk size:**
One review per chunk (Average 100-300 Tokens)

**Overlap:**
0 tokens
**Reasoning:**
We are dealing with reviews by students, each review is a self contained opinion hence we chunk at the delimiter rather than a fixed size. Reviews are under the token limit of our embedding model which means there is no reason to split the data.Overlap is 0 because mixing reviews from different students will affect the data quality.

Noise filter: A chunk is kept only if it contains at least one of the following: a numeric rating, a course code, a domain keyword (exam, grade, lecture, homework, attendance, textbook), or a sentiment keyword (loved, hated, dreaded, amazing, awful, worst, best, terrible, great, horrible, fantastic, avoid, recommend). This ensures both information-dense and emotionally expressive reviews are preserved.

Professor name handling: Professor name is stored in metadata only — it is NOT injected into the chunk text. Injecting the name into chunk text skews semantic embeddings toward the name string rather than review content. All professor-level filtering is handled exclusively at the ChromaDB metadata layer.

Each chunk is stored in ChromaDB with the following metadata fields: professor, department, course, date, rating.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**
all-MiniLM-L6-v2 via sentence-transformers

**Top-k:**
5

**Out-of-scope handler: **
Before any retrieval runs, the system checks the queried professor name against a known professor list. If the name is not found, the pipeline exits early and returns: "I don't have reviews for this professor in the current dataset." No retrieval or generation runs, eliminating hallucination risk for unknown professors.

**Query type detection: **
 The system detects whether a query is single-professor or comparative before applying filters.

If the query names a specific professor → filter by that professor in metadata, then run semantic search.
If the query mentions a course code without naming a specific professor (e.g. "Who should I take CSCI309 with?") → skip the professor filter and retrieve top-k chunks across all professors who taught that course, then let the LLM synthesize the comparison.

**Production tradeoff reflection:**

- context: The embedding model that we are currently using is a general purpose model. A model fine tuned in educational or review content would work better as it would be more efficient in handling academic jargon and course content and codes.
- Length: The embedding model has a token limit of 512 tokens. It should be able to handle review based input chunks in most cases but will fail to handle longer content.
- Latency: It is possible to run locally for one user but would require an API Hosted model for concurrent users.


---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question| Expected answer |
|---|---------|-----------------|
| 1 | Does Hardee give partial credit on exams? |Yes, multiple reviews confirm he gives partial credit if you get any part of a problem correct|
| 2 | What Strategies should i follow to do good in Bei Xie's classes? | Copy everything she writes on the slides, read the textbook chapters, and print everything since tests are open notes|
| 3 | Who should i prefer taking CSCI309 with? |Students strongly prefer Menon — praised for clear lectures and caring attitude, while Lavergne is consistently rated poorly for being disorganized, rude, and delaying grades all semester|
| 4 | is Menon strict about in-class work and will he grade you badly if you skip? |Attendance is effectively mandatory — missing easy in-class assignments hurts your grade significantly, but his overall grading is generous and he has allowed midterm retakes |
| 5 |Should I go through past quizzes and exams to prepare for Lavergne's final? |Yes — students report her final contains the exact same questions as previous quizzes, so studying past quizzes is the most effective preparation strategy|

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.cross professor retrieval contamination : In scenarios when a query mentions a course code, there can be cross contamination and different students can feel different about a specific class due to their experience with the professor.If the top-k chunks spew more towards a specific professor due to the review volume differences , there is a possibility of bias by the LLM.
This is addressed via the query type detection mechanism in the Retrieval Approach — comparative queries skip the professor filter and retrieve across all professors who taught that course.
2.For every professor, There is a higher possibility of having more negative reviews than positive ones.This causes bias. There are also chunks that contain no useful information or contain information that may mislead the LLM. 
This is addressed via the content-based noise filter in the Chunking Strategy — a chunk is only kept if it contains a numeric rating, a course code, a domain keyword or a sentiment keyword.
3.some reviews are dated spanning nearly a decade. Teaching quality changes over time.Date is stored as a metadata field per chunk. However, whether dates are consistently present and parseable in the source files has not yet been verified. Until that audit is done, recency-based filtering is a known limitation.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->
+---------------------------+
|        INGESTION          |
+---------------------------+
| Tool: Python (open())     |
| - 10 .txt files           |
| - One file per professor  |
+---------------------------+
             |
             v
+---------------------------+
|         CHUNKING          |
+---------------------------+
| Tool: Python (split())    |
| - Split on ------ delim   |
| - 1 review = 1 chunk      |
| - Professor name in       |
|   metadata only (not text)|
| - Content-based noise     |
|   filter (not word count) |
+---------------------------+
             |
             v
+---------------------------+
|  EMBEDDING + VECTOR STORE |
+---------------------------+
| Tool: sentence-transformers|
|   all-MiniLM-L6-v2        |
| Store: ChromaDB           |
| Metadata per chunk:       |
| - professor               |
| - department              |
| - course                  |
| - date (if available)     |
| - rating                  |
+---------------------------+
             |
             v
+---------------------------+
|         RETRIEVAL         |
+---------------------------+
| Tool: ChromaDB query      |
| - Out-of-scope check first|
| - Detect query type:      |
|   single-prof or compare  |
| - Single: filter by prof  |
| - Comparative: filter by  |
|   course across all profs |
| - top-k = 5               |
+---------------------------+
             |
             v
+---------------------------+
|        GENERATION         |
+---------------------------+
| Tool: Groq (LLaMA)        |
| - Retrieved chunks as     |
|   context                 |
| - Grounded answers from   |
|   reviews only            |
+---------------------------+
---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**
i will provide claude with context first by providing data from the domain and documents section.the next step is to provide claude with the chunking strategy from planning.md and a source text document like Andrew_Mudd.txt and ask it to implement ingest_and_chunk.py script containing a parse_data() function that splits the data on ------, injects the professor name into the metadata and applies the needed noise filters. i will also verify the output by printing the chunks.
**Milestone 4 — Embedding and retrieval:**
i will give claude context first , so all data from Milestone 3 and the retrieval approach from planning.md and ask it to implement an embed_and_retrieval.py script that loads the chunks into ChromaDB using the all-MiniLM-L6-v2 via sentence-transformers model storing 5 metadata fields ( professor,department,date,course,rating) per chunk. i will verify by running a test query against ChromaDB confirming comparative queries.

**Milestone 5 — Generation and interface:**
give claude context from milestone 4 data and give it grounding requirements from README and ask it to implement a generate.py script that passes the retrieved chunks as context to Groq with a system prompt that restricts the answer only from the provided reviews. I will verify by running all 5 evaluation questions and checking that responses cite specific review content and do not hallucinate information not present in the retrieved chunks.
