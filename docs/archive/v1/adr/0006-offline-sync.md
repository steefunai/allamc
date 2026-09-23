# ADR-0006 — Offline-first technician sync with idempotent commands
Status: Accepted · Decision refs: D-33, D-34, D-35

## Decision
- The technician PWA stores the next days' jobs in IndexedDB and records every action as a command
  `{op_id (UUIDv7), type, entity_id, base_version, payload, device_time}` in an outbox.
- The server applies each command in one transaction that also inserts `processed_command(tenant_id,
  op_id)`; a replay returns the stored result.
- A command whose `base_version` is stale is not applied: a `sync_conflict` row is created for the
  dispatcher and the device is told the job's current state.
- Media uploads are a separate resumable queue; a job can reach `completed_on_device` before media
  finishes, and `completed` only when required media and proof are on the server.
- Money collection and server-verified OTP require connectivity; offline closure uses signature + the
  customer dispute window.

## Consequences
- Command handlers must be deterministic given `(state, payload)`.
- The outbox format is versioned; old app versions must be able to drain their outbox after an update.
