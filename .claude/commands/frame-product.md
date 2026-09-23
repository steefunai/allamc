---
description: Stage 0 — run the discovery quiz, then write the brief, decision log and first requirements.
---

Read `kit.json`, `docs/PROCESS.md` and `docs/QUIZ_BANK.md`. You are the product architect.

1. Quiz me in rounds of at most 3 questions, following the quiz bank's order and skipping what does not
   apply. Prefer scenario questions whose answer changes the design. When I say "suggest me", give a
   recommended default with a one-line rationale; I will accept or override.
2. After each round: record every answer in the decision log as D-xx with status DECIDED / DEFAULT /
   VALIDATE, and state the design consequence in one line. Flag scope risks bluntly.
3. When the product rounds are done, draft and STOP for approval:
   - `BRIEF.md`: one line, customers/users, **one core loop**, ranked riskiest assumptions (each becomes a
     VALIDATE decision), out-of-scope list;
   - `requirements.md`: REQs as outcomes for named users, sourced to decisions; priority `now` only for
     the thin core loop;
   - the list of screens the core loop needs (for the Stage 1 prototype).
4. After approval, commit (`frame: <product>`) and update NOW.md (header: stage 1, blockers, next steps:
   build the prototype, recruit 5 test users).
Technical rounds happen only after Stage 1 unless I ask earlier.
