# MCP (v1) — Minimal Read-Only Context Layer

## Goal
MCP v1 provides controlled, read-only context for AI agents:
- Notion lifecycle pages (SoT: specs/gates/backlog/evidence)
- Repository files (code + config + docs)

No Notion writes. No script execution via MCP. No improvisation.

## Scope (locked)
**In scope**
- Notion MCP (remote): read lifecycle pages
- Filesystem MCP (local): read-only access to the repo folder

**Out of scope**
- Notion write actions (create/update)
- Shell execution (docker, migrate, seed)
- n8n triggers via MCP
- Git MCP server (v1 intentionally excluded)

## Security model (locked)
- Notion access is user-based OAuth and limited by that user’s permissions.
- Repo access is restricted to a single root folder: `/home/student/dev/theGame`
- Filesystem server is read-only (no write tools)
- Secrets remain server-side in `.env` and never in git

## Success criteria
- Agent can locate and read Notion sections 4.2–4.7.
- Agent can read repo tree and key files (`docker-compose.yml`, `backend/app/main.py`, `scripts/*`, `db/*`).
- Agent can report spec↔code mismatches without changing anything.

## Team usage rule
Agents only produce “Next Task Briefs” (checklist + evidence).
Code changes only after explicit human trigger: `EXECUTE <task-id>` (see 4.7).

