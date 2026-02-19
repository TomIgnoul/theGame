# Notion MCP — Read-only setup (Tutorial)

## 1) Principle
Notion MCP is connected via OAuth and is limited by the authenticated user’s permissions.
To enforce read-only behavior, the Notion user must have “Can view” access only.

## 2) Recommended read-only approach
- Create a dedicated Notion user (e.g., “theGame Bot”).
- Share only the project lifecycle pages with **Can view** permission:
  - 4.1 → 4.7 (platform, compose spec, runbooks, gates, backlog, roles)
  - 4.5 Evidence pages/databases
- Do NOT give edit permissions to that user.

## 3) Connect in ChatGPT (Notion MCP)
- Open ChatGPT Settings → Connectors
- Add Notion connector URL:
  - `https://mcp.notion.com/mcp`
- Complete OAuth login with the dedicated read-only Notion user.

## 4) Share policy (locked)
- Share only the project space/pages needed for execution.
- Do not share personal pages.
- Do not share pages containing secrets.

