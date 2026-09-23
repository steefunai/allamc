# QUIZ_BANK.md — Stage 0/1 discovery quiz (kit-owned)

Used by `/frame-product` and the product-builder Skill. Ask in rounds of ≤ 3 questions; prefer
scenario questions where the answer changes the design; when the owner says "suggest me", propose a
default with rationale and log it as DEFAULT. Record every answer as a decision (D-…) with status.

## Product rounds (order matters; skip what doesn't apply)
1. **Market & customer** — Who pays? Who uses daily? Which segment first? Business size? Geography,
   language, regulation?
2. **Core loop** — The one end-to-end job that must work. What happens today instead (Excel, WhatsApp,
   competitor)? What's the moment of value?
3. **Sequencing** — If several sides/segments: rank launch order. What must exist for the next side?
4. **Configurability** — Fixed model vs tenant-configured? Who configures? Templates? Versioning of
   configuration once in use?
5. **Core objects & lifecycle** — The main records and their states; mid-life changes (amend, cancel,
   renew); what must be immutable once issued?
6. **Work execution** — Intake channels; assignment; field/mobile work; offline; proof of work;
   exceptions (out-of-scope work, approvals, declines).
7. **Money** — Who is billed, how, which taxes; is this the system of record for billing? Payment
   methods; refunds/credits; accounting exports.
8. **Inventory / resources** (if any) — Stock models, tracking level, purchasing.
9. **People & permissions** — Standard roles, custom roles, scopes (branch/team/own).
10. **External parties** — Customer portal? Partner/OEM integrations? Unknown integration shapes → a port
    with adapters.
11. **Communication** — Channels, who pays per message, languages.
12. **Reporting** — The owner's top 4 questions, ranked.
13. **Business model** — Pricing metric, free tier/trial, onboarding/migration of existing data.

## Technical rounds
14. Stack preferences; who builds (owner + agents / team); hosting region & data residency.
15. Tenancy model; identity/auth; offline needs; background jobs; files; notifications.
16. Day-one invariants list confirmed (PROCESS.md §2).

## Scenario prompts (adapt)
- "Mid-contract the customer adds 5 units and removes 2 — what happens?"
- "The field worker finds a problem outside coverage — who approves, how, and what if they decline?"
- "No signal on site — what must still work?"
- "Two staff edit the same record at once — who wins?"
- "A customer disputes a completed job a week later — what evidence exists?"
- "A new competitor listing in a marketplace upsets an existing partner — what are the rules?"
