# ADR-0007 — Global person identity with consent-based links
Status: Accepted · Decision ref: D-52

## Decision
A platform-scope `person` keyed by verified E.164 phone. Tenant records (`app_user`,
`customer_contact`) link to a person through tenant-scoped `person_link`; cross-tenant use of a person's
data (T3 "all my AMCs") requires a `consent_record`. Tenants never see other tenants' links.

## Consequences
- Phone verification anywhere (login, QR request, quote approval) can create/link the person.
- DPDP obligations (purpose, withdrawal, export/deletion) are anchored on `person` + `consent_record`.
