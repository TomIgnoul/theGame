# Troubleshooting

## Notion MCP
- OAuth fails → disconnect/reconnect the connector
- Missing pages → check page sharing for the read-only user (“Can view”)
- Agent sees too much → reduce what is shared to the bot user

## Filesystem MCP
- Agent sees too much → root path is wrong (must be repo root)
- Agent can write → read-only policy misconfigured
- Agent can’t find files → wrong repo path or missing mount

