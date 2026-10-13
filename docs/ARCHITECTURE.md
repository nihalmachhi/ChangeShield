# ChangeShield model

~~~mermaid
flowchart LR
  B[Before topology] --> D[Changed-link diff]
  A[After topology] --> D
  I[Declared intents] --> P[BFS path checks]
  D --> P
  U[Unsupported config lines] --> C[Confidence and parser coverage]
  P --> R[Findings + provenance]
  C --> R
  R --> V[PASS / FAIL / NEEDS_REVIEW]
~~~

Analysis is deliberately limited to user-declared nodes and links. Each intent is evaluated against before and after snapshots. A required reachable path that disappears or an isolated pair that gains a path is a violation. Findings include both paths and changed config-line references.

Unsupported lines reduce confidence and are retained in the report. Verdicts are deterministic and explain the modeled scope; they do not prove that unparsed configuration is safe.

