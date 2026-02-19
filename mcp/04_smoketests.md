# MCP v1 Smoke Tests (must pass)

## A) Notion MCP tests
Ask the agent to:
- find and summarize:
  - “4.5 Gate Matrix”
  - “4.6 Execution Backlog”
  - “4.7 AI Agent Roles”

Pass criteria:
- agent can retrieve the right sections and summarize accurately
- agent does not propose “new specs” outside the locked design

## B) Filesystem MCP tests
Ask the agent to:
- list repo tree
- read these files:
  - `/docker-compose.yml`
  - `/backend/app/main.py`
  - `/scripts/migrate.sh`
  - `/db/migrations/001_init.sql`

Pass criteria:
- agent can read and quote relevant snippets
- agent cannot write/modify files
- agent cannot access paths outside repo root

