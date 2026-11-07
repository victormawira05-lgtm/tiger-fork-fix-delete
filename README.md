# Fork, Fix, Delete — safely test Tiger Cloud migrations

This repository is a reproducible starter for profiling a slow time-series query on an isolated Tiger Cloud fork, trying a schema/index change there, and reviewing the evidence before any cleanup. It never connects to a database on its own and does not include credentials or a real service ID.

## Included

- `.mcp.json` connects GitHub Copilot to the Tiger CLI MCP server and Tiger’s documentation MCP endpoint. The Tiger server is configured with `TIGER_READ_ONLY=prod`; tag production services `PROD` in Tiger Cloud for that guardrail to apply. Dev/test services can still be changed.
- `.github/copilot-instructions.md` gives the agent a fork-first process and requires explicit user confirmation before creating a billable fork or deleting one.
- `sql/01_profile.sql` inspects schema/indexes and captures a baseline plan.
- `sql/fix.sql` shows the hypertable conversion example and a measured-index decision point.
- `sql/02_timestamp_type_template.sql` is a commented template that requires timezone confirmation.
- `scripts/compare_plans.py` summarizes JSON EXPLAIN plans without dependencies.

## Prerequisites and setup

1. Install [Tiger CLI](https://github.com/timescale/tiger-cli) and PostgreSQL client tools (`psql`).
2. Sign in with `tiger auth login`, then verify the account/project with `tiger auth status` and `tiger project list`.
3. Open this repository in GitHub Copilot Agent Mode. Copilot reads `.mcp.json`; approve/enable the MCP servers in your client. Restart the agent session after changing MCP configuration.
4. In Tiger Cloud, tag production services `PROD`. The MCP server's `TIGER_READ_ONLY=prod` guard protects tagged production services from writes and DDL while leaving dev services available for experiments.
5. Review `.github/copilot-instructions.md` before asking the agent to inspect or alter a database.

The Tiger MCP server uses your local Tiger CLI authentication. Never commit API keys, passwords, connection strings, production data, or EXPLAIN output. Do not turn on password-returning options in service tools.

## Workflow

1. Identify the exact source service and inspect the schema, query, constraints, and existing indexes using read-only tools.
2. Ask the agent to propose a fork and wait for explicit approval. Forking can create billable resources and copies data; confirm data handling requirements first.
3. Wait for the fork to be ready and confirm its service ID is different from the source. Run all tests and mutating SQL on that fork only.
4. Adapt `sql/01_profile.sql` and `sql/00_explain.sql` to your real table/column names. Run the baseline query on the fork. `EXPLAIN ANALYZE` runs the query and can consume resources.
5. Review and adapt `sql/fix.sql`. Verify the partition column is `TIMESTAMPTZ NOT NULL`, inspect existing indexes, and review table size/foreign keys before conversion. `migrate_data => true` can take time and cause locks.
6. Run the after-plan on the same fork under comparable load/cache conditions. Compare multiple runs, not just one.
7. Review the migration and operational rollout yourself. The examples do not deploy changes to production.
8. If the fork is no longer needed, identify its exact ID and explicitly approve deletion. Never delete the source service.

Example local plan capture (PowerShell; replace only with your **fork** DSN set in the current shell):

```powershell
New-Item -ItemType Directory -Force plans | Out-Null
psql $env:TIGER_FORK_DSN -X -A -t -v ON_ERROR_STOP=1 -f sql/00_explain.sql > plans/before.json
# After the reviewed change, capture another plan:
psql $env:TIGER_FORK_DSN -X -A -t -v ON_ERROR_STOP=1 -f sql/00_explain.sql > plans/after.json
python scripts/compare_plans.py plans/before.json plans/after.json
```

Plan files are ignored by Git because they may disclose query/table names or data values. Review them locally and sanitize before sharing.

## Important limits

- The sample query/table names are illustrative. Replace them with your schema.
- Converting an existing table with `migrate_data => true` can lock it and may interact with foreign keys. Test on a fork and read the current Tiger docs first.
- A `timestamp without time zone` value has no timezone. The conversion template shows UTC only as an example; use the confirmed source timezone.
- A hypertable may already have an index on its time column. Do not add duplicate indexes without checking `pg_indexes` and measuring the actual query.
- Query timings depend on data, cache, hardware, and load. This repo does not claim a 2.3s-to-43ms result; record your own plans.
- “Delete” means the optional cleanup step for a disposable fork, only after exact-ID confirmation. It is not automated.

## References

- [Tiger CLI and MCP](https://github.com/timescale/tiger-cli)
- [Tiger Cloud fork services](https://www.tigerdata.com/docs/deploy/tiger-cloud/tiger-cloud-aws/service-management/fork-services)
- [Tiger Cloud hypertables](https://www.tigerdata.com/docs/learn/hypertables/creating-and-configuring-hypertables)
- [Tiger MCP documentation](https://d1ovb29l12vjqm.cloudfront.net/ai/latest/mcp-server/)
