# social-ops-kit

A clean open-source foundation for social publishing workflows built around two layers:
- MCP for real platform operations
- Skills for strategy, tone, review loops, and publishing SOPs

Current focus:
- Douyin
- Xiaohongshu (XHS / RedNote)

## Why this repo exists

Existing local automations were effective, but they mixed together:
- one-off debug scripts
- platform-specific hacks
- content-specific publish flows
- private environment assumptions
- strategy prompts and execution logic

This project resets that into a cleaner OSS shape.

## Design principles

1. MCP is the execution layer.
2. Skills are the strategy layer.
3. Platform adapters stay separate from content strategy.
4. Config replaces hardcoded paths, proxies, and private state.
5. Experimental hacks stay isolated, never in the stable core.

## Repository layout

- `src/social_ops_kit/`
  - `config.py` — environment-backed settings
  - `models.py` — typed shared models
  - `registry.py` — curated tool registry
  - `platforms/` — platform contracts and adapters
  - `mcp/` — MCP-facing tool manifest / server blueprint
  - `cli.py` — local inspection helpers
- `skills/`
  - reusable strategy-layer skills for Douyin and XHS
- `docs/`
  - architecture, migration inventory, roadmap, style guide
- `tests/`
  - lightweight validation for the refactor foundation

## Style rules

- Python source filenames use snake_case.
- Skill directory names use kebab-case.
- Markdown docs use kebab-case filenames.
- Stable manifest capability names use snake_case.
- Python formatting/linting is standardized in `pyproject.toml` via Ruff settings.

## Curated scope for v0

Stable core only:
- auth status
- login lifecycle
- search for notes / posts / videos / creators
- draft creation / publish workflow
- publish with optional background music where the platform supports it
- basic creator-side inspection
- comment notification / reply workflow
- private-message listing and reply workflow

Excluded from stable core for now:
- probe scripts
- theme-specific publish scripts
- destructive one-off cleanup scripts
- brittle music/debug experiments as first-class APIs

## Tool matrix

Current snapshot:
- 35 curated MCP tools total
- 35 / 35 implemented in the local runtime surface
- Douyin: 13 tools (`11 runnable`, `2 external_dependent`)
- XHS: 22 tools (`21 runnable`, `1 external_dependent`)

Maturity legend:
- `declared` — capability is part of the curated OSS contract but runtime wiring is not finished yet
- `runnable` — local runtime foundation is wired and test-covered in this repo
- `external_dependent` — wired here, but meaningfully depends on real browser session/platform state/publish environment

### Douyin

| Tool | Implemented | Maturity | Notes |
| --- | --- | --- | --- |
| `douyin_check_auth` | yes | `runnable` | Reads local login state markers |
| `douyin_start_login` | yes | `runnable` | Starts persistent QR login worker |
| `douyin_get_login_state` | yes | `runnable` | Reads login worker state |
| `douyin_stop_login` | yes | `runnable` | Stops login worker |
| `douyin_search_content` | yes | `runnable` | Normalizes Douyin search result payloads |
| `douyin_publish_image_post` | yes | `external_dependent` | Publish request is wired; final publish depends on live platform/browser state |
| `douyin_publish_image_post_with_music` | yes | `external_dependent` | Music-aware publish flow depends on live platform/browser state |
| `douyin_inspect_recent_posts` | yes | `runnable` | Parses manage-page text snapshot |
| `douyin_get_post_stats` | yes | `runnable` | Extracts metrics from manage-page text |
| `douyin_get_note_detail` | yes | `runnable` | Normalizes a creator-side note detail payload |
| `douyin_list_messages` | yes | `runnable` | Normalizes DM thread payloads |
| `douyin_reply_message` | yes | `runnable` | Builds unified reply payload/result |
| `douyin_reply_visible_comments` | yes | `runnable` | Classifies comments and drafts replies |

### XHS

| Tool | Implemented | Maturity | Notes |
| --- | --- | --- | --- |
| `xhs_check_auth` | yes | `runnable` | Reads local session markers |
| `xhs_search_content` | yes | `runnable` | Normalizes XHS search result payloads |
| `xhs_create_draft` | yes | `runnable` | Builds normalized draft request payloads |
| `xhs_get_draft` | yes | `runnable` | Reads normalized in-memory draft records |
| `xhs_list_drafts` | yes | `runnable` | Lists normalized draft records |
| `xhs_delete_draft` | yes | `runnable` | Deletes normalized draft records |
| `xhs_delete_note` | yes | `runnable` | Structures published-note delete requests |
| `xhs_update_draft` | yes | `runnable` | Updates normalized draft records |
| `xhs_publish_draft` | yes | `runnable` | Structures draft publish requests |
| `xhs_like_feed` | yes | `runnable` | Structures feed-like actions |
| `xhs_favorite_feed` | yes | `runnable` | Structures feed-favorite actions |
| `xhs_like_comment` | yes | `runnable` | Structures comment-like actions |
| `xhs_favorite_comment` | yes | `runnable` | Structures comment-favorite actions |
| `xhs_post_comment` | yes | `runnable` | Structures comment post actions |
| `xhs_create_and_publish_draft` | yes | `external_dependent` | End-to-end publish depends on live account/browser state |
| `xhs_get_my_notes` | yes | `runnable` | Normalizes creator note payloads |
| `xhs_get_note_detail` | yes | `runnable` | Normalizes a single note detail payload |
| `xhs_get_post_stats` | yes | `runnable` | Normalizes creator stats payloads |
| `xhs_get_notifications` | yes | `runnable` | Normalizes notification payloads |
| `xhs_list_messages` | yes | `runnable` | Normalizes DM thread payloads |
| `xhs_reply_message` | yes | `runnable` | Builds unified reply payload/result |
| `xhs_reply_comment` | yes | `runnable` | Validates and structures comment reply flow |

## Quick start

```bash
cd /root/social-ops-kit
python3 -m social_ops_kit.cli manifest
python3 -m social_ops_kit.cli skills
python3 -m social_ops_kit.cli doctor
```

## Configuration

Configuration is environment driven.
See `src/social_ops_kit/config.py` for the full set of variables.

Key examples:
- `SOCIAL_OPS_WORKSPACE`
- `SOCIAL_OPS_PROXY`
- `SOCIAL_OPS_DOUYIN_STATE_DIR`
- `SOCIAL_OPS_XHS_STATE_DIR`

## Open-source strategy

This repo intentionally ships both:
- MCP-oriented execution architecture
- skill-oriented strategy assets

That split keeps the project useful both to:
- agent builders who need reusable execution tools
- operators who want high-quality publishing/review workflows
