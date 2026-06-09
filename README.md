# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->
     Domain : Mcneese State University Professor Reviews

Each student has a different method of learning that works for them.  while going through college every student is faced with a situation where they end up taking a class under a professor whose method of teaching is different from what works for that specific student. There is a need for students to have access to information about the way every professor teaches, their grading style, their exam patterns and other useful info. 
This system allows students to make queries in their natural language.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

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

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->
     
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
No Overlap
**Why these choices fit your documents:**
we are dealing with reviews by students, each review is a self contained opinion hence we chunk at the delimiter rather than a fixed size. Reviews are under the token limit of our embedding model which means there is no reason to split the data.Overlap is 0 because mixing reviews from different students will affect the data quality.

Noise filter: A chunk is kept only if it contains at least 15 words. This ensures genuinely empty or meaningless reviews are dropped while preserving all substantive content regardless of the specific words used. The keyword-based approach was abandoned because plural forms, synonyms, and unexpected phrasing caused important chunks to be silently dropped.

Professor name handling: Professor name is stored in metadata only — it is NOT injected into the chunk text. Injecting the name into chunk text skews semantic embeddings toward the name string rather than review content. All professor-level filtering is handled exclusively at the ChromaDB metadata layer.

Each chunk is stored in ChromaDB with the following metadata fields: professor, department, course, date, rating.

**Final chunk count:**
141 chunks across 10 professors
---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**
all-MiniLM-L6-v2 via sentence-transformers

**Production tradeoff reflection:**

- context: The embedding model that we are currently using is a general purpose model. A model fine tuned in educational or review content would work better as it would be more efficient in handling academic jargon and course content and codes.
- Length: The embedding model has a token limit of 512 tokens. It should be able to handle review based input chunks in most cases but will fail to handle longer content.
- Latency: It is possible to run locally for one user but would require an API Hosted model for concurrent users.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**
The file metadata embedded into each chunk is passed as context to the LLM. which gives it structured facts to cite.
Before doing anything else each query is classified into a professor or class query. This helps taper the semantic search process to more relevant chunks. 
Strict instructions are provided in the genrate.py Script as a prompt which is passed to the LLm.
STRICT GROUNDING RULES:
- Answer ONLY using the information provided in the retrieved reviews below.
- Do NOT use your general training knowledge about professors, universities, or teaching.
- If the retrieved reviews do not contain enough information to answer the question, say exactly:
  "I don't have enough information in the current reviews to answer that question."
- Do NOT make up or infer anything not explicitly stated in the reviews.
- Do NOT give advice beyond what the reviews actually say.
**How source attribution is surfaced in the response:**

Strict instructions are provided in the genrate.py Script as a prompt which is passed to the LLm.
SOURCE ATTRIBUTION RULES:

- After your answer, always include a "Sources:" section.
- List each review you drew from, formatted as:
  - [Professor Name] | [Course] | [Date] | Rating: [X/5]
- Only list sources you actually used in your answer.

Keep your answer clear, helpful, and concise.
---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Does Hardee give partial credit on exams? |Yes, multiple reviews confirm he gives partial credit if you get any part of a problem correct | System confrimed that partial credit does exist but noted that it is stated in a general context not specifically about exam |Relevant |Partially accurate - it states that partial credit is given , buthedged on whether it applies specifically on exams. This depicts that the response are grounded but are strictly tied to the input data in the chunks.|
| 2 |What Strategies should i follow to do good in Bei Xie's classes? | Copy everything she writes on the slides, read the textbook chapters, and print everything since tests are open note|Copy everything she writes, read chapters to understand material, print everything since tests are open notes/open everything, and keep group projects simple | Relevant| Accurate - output matches the expected output and adds additional helpful information.|
| 3 |Who should i prefer taking CSCI309 with? | Students strongly prefer Menon — praised for clear lectures and caring attitude, while Lavergne is consistently rated poorly for being disorganized, rude, and delaying grades all semester|Reterived only the reviews from Lavergne CSCI309.The output summarizes the negative reviews against her but provides no suggestion for taking the class with Menon. | off-target - Only retrieved chuncks related to Lavergnes CSCI 309 and left out the chucks corresponding to Menon's CSCI309. This could be because fo the fact Lavergne has more relevant chunks (Chucks have a lower distance for seemantic search) or the differnece in the volume of relevant chunks for Menon|Partially correct - The information provided for Lavergne's CSCI309 is relevant but Menon is Completely missed due to chunk retrieval failure. |
| 4 |is Menon strict about in-class work and will he grade you badly if you skip? | Attendance is effectively mandatory — missing easy in-class assignments hurts your grade significantly, but his overall grading is generous and he has allowed midterm retakes| The system returns info from the chunks explaining how there is a lot of high credit things that need the students to actively particcipate in the class|Relevant |accurate |
| 5 | Should I go through past quizzes and exams to prepare for Lavergne's final?| Yes — students report her final contains the exact same questions as previous quizzes, so studying past quizzes is the most effective preparation strategy| Yes, go through past quizzes and exams — the final contains the exact same questions| relevant|accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**
Who should I prefer taking CSCI309 with?
**What the system returned:**
The system returned only reviews from Lavergne completely missing Menon.It provided a detailed conclusion of the negative reviews for Lavergne but failed to provide the suggestion for Menon.
**Root cause (tied to a specific pipeline stage):**
The failure is in the retrieval stage. detect_query_type() in embed_and_retrieve.py picked up CSCI309 as a course code and filtered ChromaDB strictly by that course metadata field. Menon's reviews were ingested under CSCI180 and CSCI274 — he has no chunk tagged CSCI309. So his chunks never entered the candidate pool and semantic search had nothing to rank against Lavergne.
**What you would change to fix it:**
Add a professor-to-course mapping at ingestion time so that comparative queries can retrieve by professor name in addition to course code. Alternatively, inject cross-reference context into the summary chunks (e.g. "students compared this professor to Menon for CSCI309") so semantic similarity can surface the connection even without a matching metadata field.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**
TWriting down the professor name handling decision before coding saved me from a bug I wouldn't have noticed until retrieval. If the name was injected into chunk text, embeddings would pull toward the name string instead of the review content. Having it in planning.md meant it was applied consistently in ingest_and_chunk.py from the start rather than fixed later.
**One way your implementation diverged from the spec, and why:**
The spec described a keyword-based noise filter that kept chunks only if they contained a numeric rating, a course code, or a domain/sentiment keyword. During Milestone 3 implementation this was abandoned after it silently dropped a substantive Lavergne review that contained no trigger keywords. The filter was replaced with a simple 15-word minimum count, which preserved all meaningful reviews without risk of false negatives. The planning.md was updated to document this change.
---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
The Chunking Strategy section from planning.md, a sample professor .txt file (Andrew_Mudd.txt), and a request to implement ingest_and_chunk.py with a --- delimiter split, metadata-only professor name handling, and the keyword-based noise filter.
- *What it produced:*
A working ingestion script with parse_header(), parse_review_block(), and a keyword-based passes_noise_filter() function.
- *What I changed or overrode:*
After running the script and finding that the keyword filter silently dropped a valid Lavergne review, I replaced the keyword filter with a 15-word minimum count filter and updated planning.md to reflect the change.

**Instance 2**

- *What I gave the AI:*
The completed ingest_and_chunk.py, the Retrieval Approach section from planning.md, and a request to implement embed_and_retrieve.py using all-MiniLM-L6-v2 and ChromaDB with 5 metadata fields, cosine distance, and query type detection.
- *What it produced:*
A retrieval pipeline with embed_and_store(), detect_query_type(), is_out_of_scope(), and retrieve() using L2 distance (ChromaDB default).
- *What I changed or overrode:*
After running evaluation queries and finding distance scores above 0.5 (failing the checkpoint requirement), I directed the switch from L2 to cosine distance by adding hnsw:space: cosine to the ChromaDB collection metadata, which brought scores into the expected range.
