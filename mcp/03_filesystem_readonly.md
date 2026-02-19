# Filesystem MCP — Read-only repo access (Tutorial)

## 1) Goal
Allow agents to read repo files for:
- config checks (compose, scripts)
- contract checks (endpoints)
- doc checks (gates/evidence)

No write, no delete, no execute.

## 2) Policy (locked)
- Root path: `/home/student/dev/theGame`
- Read-only tools only
- No access outside repo root

## 3) Client note
Filesystem MCP configuration depends on the AI client (ChatGPT vs Cursor/VS Code vs Claude).
In v1 we document the policy and smoke tests; actual client wiring is documented per tool when chosen.

