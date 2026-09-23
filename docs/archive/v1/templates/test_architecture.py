"""Architecture fitness tests — BOOT-001 installs this as backend/tests/architecture/test_architecture.py.

These are the mechanical guarantees behind CLAUDE.md §2. Do not weaken them to make a slice pass;
if a table genuinely is platform-scope, add it to PLATFORM_TABLES with an ADR reference.
Fixtures `owner_conn` (owner role) and `app_conn` (allamc_app role) come from tests/conftest.py.
"""
from __future__ import annotations

import pytest
from sqlalchemy import BigInteger, Numeric, text

from app.common.db import Base
from app.wiring import import_all_models

import_all_models()  # every module's models.py must be registered on Base.metadata

PLATFORM_TABLES = {  # DATA-001 §8
    "person", "consent_record", "starter_template", "plan", "config_value", "alembic_version",
}
PLATFORM_PREFIXES = ("procrastinate_",)


def _is_platform(name: str) -> bool:
    return name in PLATFORM_TABLES or name.startswith(PLATFORM_PREFIXES)


def _tenant_tables() -> list[str]:
    return [t.name for t in Base.metadata.sorted_tables if not _is_platform(t.name) and t.name != "tenant"]


@pytest.mark.unit
def test_every_tenant_owned_table_has_tenant_id() -> None:
    missing = [n for n in _tenant_tables() if "tenant_id" not in Base.metadata.tables[n].c]
    assert not missing, f"tables without tenant_id (INV-01): {missing}"


@pytest.mark.unit
def test_no_float_or_numeric_columns_anywhere() -> None:
    # Float is a subclass of Numeric in SQLAlchemy; both are banned (INV-06).
    bad = [
        f"{t.name}.{c.name}"
        for t in Base.metadata.sorted_tables
        for c in t.columns
        if isinstance(c.type, Numeric)
    ]
    assert not bad, f"float/numeric columns are forbidden, use integer paise/bp/milli: {bad}"


@pytest.mark.unit
def test_money_columns_are_bigint() -> None:
    bad = [
        f"{t.name}.{c.name}"
        for t in Base.metadata.sorted_tables
        for c in t.columns
        if c.name.endswith(("_paise", "_milli")) and not isinstance(c.type, BigInteger)
    ]
    assert not bad, f"*_paise / *_milli columns must be BIGINT: {bad}"


@pytest.mark.integration
def test_rls_enabled_forced_and_policied(owner_conn) -> None:
    rows = owner_conn.execute(text("""
        SELECT c.relname, c.relrowsecurity, c.relforcerowsecurity,
               EXISTS (SELECT 1 FROM pg_policies p WHERE p.tablename = c.relname) AS has_policy
        FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public' AND c.relkind = 'r'
    """)).all()
    state = {r.relname: r for r in rows}
    problems = []
    for name in _tenant_tables() + ["tenant"]:
        r = state.get(name)
        if r is None:
            problems.append(f"{name}: not migrated")
        elif not (r.relrowsecurity and r.relforcerowsecurity and r.has_policy):
            problems.append(f"{name}: rls={r.relrowsecurity} force={r.relforcerowsecurity} policy={r.has_policy}")
    assert not problems, "RLS problems (INV-01): " + "; ".join(problems)


@pytest.mark.integration
def test_runtime_role_cannot_bypass_rls(owner_conn) -> None:
    role = owner_conn.execute(text(
        "SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname = 'allamc_app'"
    )).one()
    assert not role.rolsuper and not role.rolbypassrls
    owned = owner_conn.execute(text(
        "SELECT count(*) FROM pg_tables WHERE schemaname = 'public' AND tableowner = 'allamc_app'"
    )).scalar_one()
    assert owned == 0, "allamc_app must not own tables (owners bypass RLS unless FORCEd)"


@pytest.mark.integration
def test_unset_tenant_context_sees_no_rows(app_conn, seeded_two_tenants) -> None:
    # seeded_two_tenants inserts at least one branch per tenant through the owner role.
    count = app_conn.execute(text("SELECT count(*) FROM branch")).scalar_one()
    assert count == 0, "queries without app.tenant_id must see nothing"
