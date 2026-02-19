# MCP v1 Overview (Read-only)

## What is MCP?
MCP (Model Context Protocol) is a standard that connects AI clients to external context sources via “servers”.

## Why MCP in this project?
- Notion is our Source of Truth (lifecycle, gates, evidence, backlog).
- The repo is the execution layer (code/config/scripts).
- MCP v1 prevents agents from guessing.

## V1 setup (2 connectors)
1) Notion MCP (remote): reads lifecycle pages.
2) Filesystem MCP (local): reads the repo folder (read-only).

## V1 boundaries (non-negotiable)
- No Notion writes
- No shell execution
- No n8n triggers
- Read-only repo access

