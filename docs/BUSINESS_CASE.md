# Business case: EvolSynth API

**Test data for RAG and LLM systems, generated from your own documents.**

## Who buys this

The buyer is the engineering or product lead who has a retrieval-augmented generation (RAG) assistant in a pilot and needs to decide whether it is good enough to ship. The users are ML engineers and QA analysts. The organisation has documents (policies, manuals, contracts, product docs) but no labelled question-and-answer set to test against.

## The problem and what it costs

Generative AI pilots often stall between demo and production. In July 2024 Gartner predicted that at least 30% of GenAI projects would be abandoned after proof of concept by the end of 2025, citing poor data quality, inadequate risk controls, escalating costs or unclear business value ([Gartner, Jul 2024](https://www.gartner.com/en/newsroom/press-releases/2024-07-29-gartner-predicts-30-percent-of-generative-ai-projects-will-be-abandoned-after-proof-of-concept-by-end-of-2025)). In January 2026 Gartner reported that the actual figure was at least 50% ([Gartner, 2026](https://www.gartner.com/en/articles/genai-project-failure)). Gartner gave no published method for either figure, so treat them as direction, not measurement.

One practical reason is that teams can't show the system works. Writing a test set by hand means subject-matter experts reading documents and drafting questions with reference answers. That is slow, and it tends to produce easy questions that look up a single fact, which flatters the system.

## How the repo solves it

| Need | What in the repo does it |
|---|---|
| Questions grounded in the real corpus | Document upload and base-question extraction in `api/services/` |
| Harder questions, not just lookups | The Evol-Instruct method from the WizardLM paper ([Xu et al., 2023](https://arxiv.org/abs/2304.12244)), with simple, multi-context, reasoning and complex evolutions, run as a LangGraph workflow |
| Reference answers and contexts | Each evolved question comes with its answer and source contexts (`evolved_questions`, `question_answers`, `question_contexts` in the API output) |
| A quality check on the generated set | `POST /evaluate`: an LLM-as-judge pass over the generated data |
| Something a non-engineer can use | The Next.js front end in `frontend/`, with Redis caching and Docker deploy files |

## Use-case scenarios

All of these organisations are fictional.

1. **An insurer's claims-policy assistant.** Before rollout to adjusters, the team generates 300 evolved questions from 40 policy wordings. The multi-context questions ("Does water damage from a burst pipe in an unoccupied home fall under the same exclusion as flood?") expose retrieval gaps that single-fact questions missed.
2. **A software vendor's support bot.** Each product release changes the docs. The team regenerates the evaluation set on every docs build and blocks a release if answer quality drops.
3. **A law firm's knowledge-management group** compares two chunking strategies on the same evolved question set, instead of arguing from examples.

## ROI: a worked model (illustrative)

These figures are **illustrative assumptions**. Replace them with your own.

| Input | Value | Basis |
|---|---|---|
| Questions needed per evaluation set | 300 | Assumption |
| Expert minutes to write one question with an answer and its source, by hand | 15 | Assumption |
| Expert minutes to review one generated question | 3 | Assumption |
| Evaluation sets built per year (new corpora and major releases) | 6 | Assumption |
| Expert hourly cost | US$70 | BLS May 2024 median for data scientists is $112,590 a year, about $54 an hour ([BLS](https://www.bls.gov/ooh/math/data-scientists.htm)). Multiplied by an assumed 1.3 for overhead. |

By hand: 300 × 15 min = 75 hours per set. With generation plus review: 300 × 3 min = 15 hours per set. Saving: 60 hours × 6 sets = **360 hours a year, about US$25,000**, before LLM API costs. The larger benefit isn't counted: a test set that exists before launch, so the go/no-go decision rests on measurements rather than a demo.

## Path to production

1. Point it at a real corpus and have a domain expert review a sample of the generated questions. Record the acceptance rate.
2. Run the accepted set against the target RAG system with an evaluation framework (RAGAS or similar), and record a baseline score.
3. Add the generation and evaluation step to CI for the RAG system's repo, so the set is refreshed when documents change.
4. Add authentication, per-tenant storage and cost limits on LLM calls before sharing the service across teams.

## Risks and limits

- The questions and reference answers are written by an LLM. Without expert review they can be wrong, and an evaluation set with wrong answers is worse than none.
- An LLM judge has its own biases. Spot-check it against human grades.
- Sending confidential documents to a hosted LLM may not be allowed. Use a private model endpoint where needed.
- The performance claims in the main README come from the repo's own benchmarks, not an independent test.

## Sources

- Gartner press release (Jul 29, 2024): https://www.gartner.com/en/newsroom/press-releases/2024-07-29-gartner-predicts-30-percent-of-generative-ai-projects-will-be-abandoned-after-proof-of-concept-by-end-of-2025
- Gartner, "Why 50% of GenAI Projects Fail" (2026): https://www.gartner.com/en/articles/genai-project-failure
- Xu et al., *WizardLM: Empowering Large Language Models to Follow Complex Instructions* (2023): https://arxiv.org/abs/2304.12244
- U.S. Bureau of Labor Statistics, Data Scientists: https://www.bls.gov/ooh/math/data-scientists.htm
