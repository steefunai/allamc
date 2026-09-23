---
product: {{PRODUCT}}
mode: discovery            # discovery | active | maintain | paused
stage: 0                   # 0 Frame … 6 Launch (docs/PROCESS.md §2)
gate_blockers: 3           # number of unmet exit-gate criteria for the current stage
in_progress: none          # slice id or none
verify: unknown            # green | red | unknown (result of the last full verify.sh run)
ui_debt: 0                 # slices at "backend-complete, UI pending"
last_user_session: never   # YYYY-MM-DD or never
last_weekly_review: never  # YYYY-MM-DD or never
waiting_on_owner: 0        # open items in "Waiting on you"
updated: YYYY-MM-DD
---
# NOW.md — {{PRODUCT}} (read this first, every session)

Updated by the agent after every slice, weekly review and stage gate. One screen maximum.

**Stage gate blockers:**
- Brief not written
- Core loop not named
- Riskiest assumptions not ranked

## In progress
- none

## Next (ranked; refill with /propose-slices when fewer than 3)
1. Run /frame-product

## Waiting on you
-

## Open VALIDATE items
-
