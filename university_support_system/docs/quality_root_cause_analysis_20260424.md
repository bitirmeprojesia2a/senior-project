# Quality Root Cause Analysis - 2026-04-24

## Scope

This note summarizes the current root-cause analysis for answer quality issues
observed in the balanced-profile benchmark run:

- Benchmark JSON: `tests/archive/benchmarks/quality_benchmark_20260424_151903.json`
- Benchmark summary:
  - Department accuracy: `25/25`
  - Generation mode accuracy: `23/25`
  - Key fact coverage: `53/100`
  - Clean quality: `25/25`

The goal is not to explain every weak answer separately, but to identify the
systemic reasons they happen repeatedly.

## Main Conclusion

The current quality problem is not caused by a single component.

The strongest root-cause chain is:

1. Query is routed to the correct department.
2. Inside that department, the wrong specialist agent is often selected.
3. Retrieval returns a mixed candidate pool and relies on late penalties.
4. Evidence selection compresses the context too aggressively.
5. Specialist/global synthesis operate on partial evidence or prior summaries.
6. Final filtering/surfacing can collapse multi-department answers into a
   single surviving branch.

In short:

- Routing is mostly working.
- Department-internal expert selection is not.
- Retrieval heuristics are too brittle for procedural/paraphrase questions.
- Evidence and synthesis are over-compressed.
- Final surfacing can hide useful branch outputs.

## High-Confidence Findings

### 0. A hidden A2A specialist-discovery failure was masking itself as "endpoint missing"

After the first routing/dispatch fixes were deployed, `Q18`, `Q22`, `Q23`, and
`Q25` suddenly degraded into `a2a_transport_fallback` responses from the
student-affairs branch. That looked like a new routing regression at first, but
the real cause was lower in the stack:

- `student_affairs` started selecting `registration_agent` more often, which was
  correct.
- `HttpA2ASpecialistTransport._resolve_endpoint()` then queried the agent
  registry.
- During that query, SQLAlchemy mapper initialization could fail because some
  services boot with only a partial ORM import graph loaded.
- The exception was logged best-effort and swallowed, so registry resolution
  returned `None`.
- That surfaced as `a2a_specialist_endpoint_missing`, even though the
  `registration_agent` service was healthy, registered, and advertising the
  correct AgentCard.

Concrete validation:

- Local direct check before the fix: `_resolve_endpoint(RegistrationAgent())`
  returned `None` and logged a mapper error around `Student -> Tuition`.
- Root cause fix: `src/db/connection.py` now imports the full `src.db.models`
  graph before creating the first session factory.
- Local direct check after the fix: `_resolve_endpoint(RegistrationAgent())`
  returned `http://agent-student-registration:8120`.
- Re-run subset benchmark (`Q5`, `Q18`, `Q22`, `Q23`, `Q25`) recovered from
  `2/5` mode accuracy to `4/5`, and removed the transport fallback collapse.

This is important because it means some "quality" failures were actually
integration failures in disguise.

### 0. Cross-department dispatch reuses one shared task type for all branches

In parallel queries, `dispatch_to_departments()` passes the same
`routing.task_type` to every selected department orchestrator.

That is a structural problem because a multi-department question often needs
different specialist types per department.

Example:

- `Q5` has routing task type `tuition_query`.
- That makes sense for finance.
- But the same shared task type is also sent to `student_affairs` and
  `academic_programs`, even though those branches need registration/international
  logic rather than tuition logic.

Concrete benchmark evidence from `quality_benchmark_20260424_151903.json`:

- `Q5`: `routing_task_type=tuition_query`
- `Q18`: `routing_task_type=academic_query`
- `Q22`: `routing_task_type=course_query`
- `Q25`: `routing_task_type=academic_query`

This helps explain why many correctly routed multi-department queries still hit
the wrong specialists.

Relevant files:

- `src/orchestrators/department_dispatch.py`
- `src/orchestrators/department.py`
- `src/routing/routing_policy.py`

### 1. Student affairs internal task-to-agent mapping is structurally wrong

`student_affairs` uses a coarse task map:

- `REGISTRATION_QUERY -> registration_agent`
- `ACADEMIC_QUERY -> graduation_agent`
- `COURSE_QUERY -> graduation_agent`
- `PROCEDURE_QUERY -> internship_agent`

This is a major mismatch.

Examples:

- `Q18` (exam grade objection process) is procedural/admin, but can easily fall
  into `graduation_agent`.
- `Q22` (copy/discpline process) is not an internship problem, yet
  `PROCEDURE_QUERY` in student affairs maps to `internship_agent`.
- `Q25` (teacher did not enter grades) is procedural/student affairs follow-up,
  but `graduation_agent` receives it because task typing is too coarse.

Impact:

- Wrong specialist prompt
- Wrong retrieval bias
- Wrong source selection
- Weak or irrelevant answer even when department routing is correct

Relevant files:

- `src/routing/routing_policy.py`
- `src/orchestrators/department_factories.py`
- `src/orchestrators/department.py`

### 2. Query/task typing is too coarse for student affairs

`detect_task_type()` groups many different intents under `ACADEMIC_QUERY` or
`PROCEDURE_QUERY`.

For student affairs, these all collapse together:

- note objection
- discipline / copy
- diploma / graduation
- transcript / documents
- relation cutting / withdrawal
- grade-entry issue

This means the department is correct but the specialist is still wrong.

Impact:

- Strong benchmark department accuracy hides specialist-selection failure.
- Many bad answers start before retrieval.

Relevant files:

- `src/routing/routing_policy.py`
- `src/core/constants.py`

### 3. Retrieval penalties are applied too late

Retriever flow today is roughly:

1. preprocess query
2. collect hybrid candidates
3. deduplicate
4. apply some score biases
5. sort candidates
6. rerank top candidates
7. apply `_apply_source_relevance()` only in `_finalize_results()`

That means source relevance penalties do not shape the reranker candidate pool
early enough. Bad candidates can already enter the reranker window and survive
to top-k.

This is especially harmful for:

- `Q1` (muafiyet + derslere devam)
- `Q20` (diploma kaybi + e-devlet/YOKSIS)
- `Q22` (copy/discpline)
- `Q25` (notlar sisteme girilmemis)

Relevant files:

- `src/rag/retriever.py`
- `src/rag/search_planner.py`

### 4. Fallback collections only help when primary retrieval is empty

Current logic only tries fallback collections if primary collections produce no
candidates at all.

That is too weak.

Real failure mode in this project is not "zero candidates"; it is
"non-empty but wrong candidates".

So if primary retrieval returns a weak but non-empty set, better fallback
collections are never queried.

This likely contributes to:

- `Q1` using a yatay gecis announcement but missing muafiyet process facts
- `Q20` missing the YOKSIS side
- `Q25` retrieving generic registration/FAQ text instead of grade-entry guidance

Relevant file:

- `src/rag/retriever.py`

### 5. Evidence selection is too lexically biased and too compressed

Evidence path currently does all of the following:

- computes term overlap / topic coherence
- selects a few evidence sentences
- falls back to first 2 sentences if scoring is weak
- builds at most a few context chunks
- limits content length per chunk

This is fragile for:

- paraphrase questions
- multi-step procedures
- questions where the right answer needs multiple small clauses

Examples:

- `Q23` (leave university / withdraw)
- `Q24` (return after freeze)
- `Q25` (grades not entered)
- `Q17` (from course registration to advisor approval)

This is also why some correct retrieval still becomes incomplete synthesis.

Relevant files:

- `src/quality/evidence.py`
- `src/agents/base.py`

### 6. Specialist/global synthesis are operating on compressed summaries

Specialist LLM often sees only compressed evidence chunks.
Then global synthesis may see:

- department answer summaries
- limited snippets
- extracted facts

instead of full high-quality source context.

So the second LLM sometimes synthesizes the first LLM's summary, not the real
source material.

This amplifies upstream mistakes rather than correcting them.

Relevant files:

- `src/agents/base.py`
- `src/orchestrators/synthesis_utils.py`
- `src/orchestrators/main.py`

### 7. Final response filtering can collapse multi-department queries into one branch

`filter_low_confidence_responses()` removes low-confidence and no-info branches
before final composition.

That is reasonable in principle, but for cross-department queries it can hide
partially useful branches and leave a single strong VT answer.

This seems to be the clearest explanation for `Q5`:

- routing selected `academic_programs + student_affairs + finance`
- LLM usage shows academic/student branches ran
- final answer surfaced only the finance VT fee table

So the final user answer can look like a one-department answer even after
multi-department work was done.

Relevant files:

- `src/orchestrators/response_utils.py`
- `src/orchestrators/main.py`
- `src/orchestrators/user_response_builders.py`

### 8. Cleanup/claim-guard do not solve the important failure classes

Current cleanup stack helps with:

- prompt leakage
- fake office/portal names
- repeated boilerplate
- some foreign word leakage

But it does not reliably solve:

- contradictory numbers or time limits
- internally inconsistent answers
- wrong-but-grounded statements
- generic fallback phrasing when actionable guidance is expected

Examples:

- `Q2` wrong minimum grade (`CB` instead of `CC`)
- `Q18` contradictory time windows
- `Q19` malformed and mixed conditions

Relevant files:

- `src/quality/claim_guard.py`
- `src/orchestrators/response_utils.py`

### 9. Query expansion is broad and can drag retrieval off target

`QueryPreprocessor` synonym expansion is helpful for recall, but it is also
broad enough to pull adjacent topics into the search.

Procedural detection is also simple:

- `procedural`
- `factual`
- otherwise `general`

This is not expressive enough for the benchmark's harder categories, especially:

- process-chain
- paraphrase
- mixed condition/procedure

Relevant file:

- `src/rag/query_preprocessor.py`

### 10. There is a configuration/implementation mismatch around reranker policy

Environment flags exist for skipping reranker in some procedural cases, but the
actual `_should_skip_reranker()` implementation currently only skips when
`len(candidates) <= top_k`.

So the runtime behavior is not aligned with what the environment suggests.

That does not explain all quality failures, but it is a real architecture
mismatch and makes tuning harder.

Relevant files:

- `src/core/config.py`
- `src/rag/retriever.py`
- `.env`

## Benchmark Questions Best Explained By Each Root Cause

### Wrong specialist selection

- `Q18`
- `Q22`
- `Q25`
- partly `Q20`

### Weak candidate pool / late source penalties

- `Q1`
- `Q20`
- `Q22`
- `Q25`

### Evidence compression / paraphrase weakness

- `Q17`
- `Q23`
- `Q24`
- `Q25`

### Cross-department response collapse

- `Q5`
- partly `Q6`

### Synthesis inconsistency / cleanup limits

- `Q2`
- `Q18`
- `Q19`
- `Q21`

## Prioritized Fix Order

If the goal is maximum benchmark lift with minimum churn, the likely best order is:

1. Stop sending one shared task type to all parallel departments.
   - Derive task type per department branch, or let each department infer its
     own type from query + department context.

2. Fix student affairs internal task-to-agent mapping.
   - Split discipline / exam objection / grade-entry / withdrawal / graduation
     more explicitly.
   - Stop mapping all `PROCEDURE_QUERY` to `internship_agent`.

3. Improve task typing for student affairs.
   - Add finer-grained intent classes or at least deterministic routing markers
     for:
     - discipline
     - note objection
     - grade-entry problem
     - withdrawal / relation cutting
     - diploma / graduation

4. Move source relevance penalties earlier in retrieval.
   - Apply query-specific exclusion/boost logic before reranker candidate window
     is fixed.

5. Change fallback behavior from "only on zero candidates" to
   "also on weak/off-topic primary candidates".

6. Relax evidence compression for process/paraphrase questions.
   - More evidence items
   - Better sentence selection
   - Less lexical-overlap dependence

7. Prevent single-branch VT collapse in cross-department final surfacing.
   - If multiple departments ran and at least two gave usable outputs, do not
     silently collapse to one branch without explicit reason.

## Working Hypothesis

The strongest current hypothesis is:

- The single highest-impact defect is wrong student-affairs specialist selection.
- The second biggest defect is late-stage retrieval shaping.
- The third is evidence/synthesis over-compression for procedural and paraphrase
  questions.

Embedding model and reranker quality may still matter, but the current evidence
suggests architecture and flow errors are the bigger problems first.

## Second-Opinion Challenges

An independent second review challenged and refined the current diagnosis in a
useful way:

1. Wrong student-affairs agent mapping may be a major defect, but not the only
   root cause.
   - If all agents still share weak retrieval/source policies, mapping fixes
     alone will not fully solve the failures.

2. "Correct department" is not strong evidence that routing is good enough.
   - The real failure may be sub-domain routing, source-family routing, or
     answer-template routing inside the department.

3. Weak answers may come more from candidate generation than reranking.
   - If the right document family never enters the candidate pool, better
     reranker timing will not recover it.

4. Process questions may need structure, not just more context.
   - Many failures look like missing slots:
     - actor / unit
     - deadline
     - required document
     - submission channel
     - decision authority
     - exception / fallback

5. Cross-department answers should likely be evaluated by required branch
   coverage, not just "best surviving branch".

## Additional Hidden Risks

These were elevated after the second review:

- Missing source-family constraints
  - Some question classes should strongly prefer certain source families before
    generation:
    - discipline / objection / petition / form / academic calendar / regulation

- No contradiction-resolution layer
  - The system currently has no strong mechanism to detect and resolve
    conflicting facts before prose generation.

- Numeric/date validation is too weak
  - Cleanup helps style, not factual consistency.

- Task taxonomy is too flat
  - `ACADEMIC_QUERY`, `COURSE_QUERY`, `PROCEDURE_QUERY` are not expressive
    enough for this domain.
