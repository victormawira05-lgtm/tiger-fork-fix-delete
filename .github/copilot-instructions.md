# Safe Tiger Cloud database workflow

This repository is a workflow template. Treat every real database as production unless the user explicitly identifies it as a disposable test fork.

## Required order

1. Start with documentation and read-only inspection. Identify the exact service ID, table, column types, constraints, row counts, query, and current query plan. Do not request or print passwords, connection strings, or secrets.
2. Before using `service_fork`, tell the user which source service will be forked, the fork name, that the fork may incur cost, and whether its copied data contains sensitive or regulated information. Wait for the user's explicit go-ahead.
3. Fork only the user-named service. Wait until the fork is ready. Verify the fork ID differs from the source ID and all mutating SQL is targeted at that fork. Do not make schema/data changes to the source service.
4. Review proposed SQL with the user before applying it. Run `EXPLAIN` first. Use `EXPLAIN ANALYZE` only on the isolated fork because it executes the query. Save before/after plans and compare results.
5. Never promote changes to production automatically. Provide a migration plan and rollback considerations for the user to review separately.
6. Before `service_delete`, independently verify the exact target is the disposable fork, state its exact ID and name, and ask the user to confirm deletion. Never delete the source service. Do not infer confirmation from earlier approval to create the fork.

## Database safety

- Never run DDL, DML, restore, or other mutating commands against production through MCP.
- A timestamp conversion must state the assumed timezone explicitly. Do not guess whether naive timestamps represent UTC or local time.
- Converting a populated table with `migrate_data => true` can take a long time, lock the table, and interact with foreign keys. Check the official docs and table constraints first.
- Inspect existing indexes before creating any. A hypertable may already have an index on its partitioning column. Add indexes only when the measured workload justifies them.
- Avoid claiming a speedup without recorded plans from the actual before/after runs.
- Never expose connection strings, passwords, API credentials, or customer data in logs, screenshots, commits, or generated reports.
