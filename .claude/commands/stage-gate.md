---
description: Check the current stage's exit gate and move the product to the next stage if it is met.
---

Read `NOW.md`, `docs/PROCESS.md` §2 and the documents in `kit.json`. For the current stage, list each
exit criterion as MET / NOT MET with evidence (file, commit, feedback note, screenshot). Do not accept a
criterion without evidence.

If all are MET: propose the next stage's first actions and the NOW.md header change; STOP for the owner to
review the evidence and approve; only then commit `stage: <n> → <n+1>`. Never move a stage without approval. If not: update `gate_blockers` and the blockers list in NOW.md with the
missing items and who owns each (agent or owner). Also report VALIDATE decisions still open for this stage.
