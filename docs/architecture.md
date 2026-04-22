# Architecture

## Core idea

This project is intentionally split into two layers.

### 1. MCP execution layer

The MCP layer should expose only stable, reusable, open-source-safe capabilities:
- auth status
- login lifecycle
- search
- publish lifecycle
- background-music-aware publishing where supported
- creator inspection
- notification / comment reply
- private-message listing and reply

It must not expose:
- debug probes
- theme-specific content scripts
- destructive hacks without strong identifiers
- private environment assumptions

### 2. Skill strategy layer

Skills carry:
- copy heuristics
- title rules
- tone rules
- publish checklists
- post-review loops

Skills must not contain platform execution logic.

## Package boundaries

- `social_ops_kit.config`
  - environment-backed settings only
- `social_ops_kit.models`
  - shared data structures and metadata
- `social_ops_kit.registry`
  - curated stable OSS tool surface
- `social_ops_kit.platforms.douyin`
  - Douyin capability contracts
- `social_ops_kit.platforms.xhs`
  - XHS capability contracts
- `social_ops_kit.mcp`
  - MCP-facing manifest / server blueprint

## What changed from the old local setup

Old local setup issues:
- flat script sprawl
- repeated browser/session code
- hardcoded `/root`, `/tmp`, proxy, and profile paths
- content-specific publishing logic mixed with general platform logic
- experiments mixed into stable flows

New repo direction:
- keep only stable core capabilities
- move strategy into skills
- isolate experimental capabilities for later opt-in modules
- make config explicit and portable
