# Phase 1 Runtime Migration Plan

> For Hermes: use subagent-driven-development to execute this plan task-by-task.

Goal: migrate the stable, actually working Douyin and Xiaohongshu execution flows into social-ops-kit with unified filenames, module boundaries, and code style.

Architecture: keep platform execution code in small typed Python modules under src/social_ops_kit/platforms/. Phase 1 only ports capabilities backed by real existing runtime code. Contract-only capabilities without stable source remain documented but unimplemented until a real source exists.

Tech stack: Python 3.11, Playwright-backed adapters, JSON state helpers, Markdown skills, pytest.

---

## Naming and style rules

- Python modules: snake_case.py
- Python packages/directories: snake_case
- Skill directories: kebab-case
- Docs: kebab-case.md
- Stable tool names: snake_case
- Max line length: 100
- Double quotes in Python

---

## Phase 1A: foundation modules

### Task 1: Douyin runtime foundation
Objective: create clean reusable Douyin runtime modules before porting behavior.

Files:
- Create: src/social_ops_kit/platforms/douyin/browser.py
- Create: src/social_ops_kit/platforms/douyin/state.py
- Create: src/social_ops_kit/platforms/douyin/login.py
- Test: tests/test_douyin_state.py

Steps:
1. Add DouyinPathSet and JSON state helpers.
2. Add browser launch config dataclasses.
3. Add login state reader/writer wrappers.
4. Add tests for path generation and JSON roundtrip.

### Task 2: XHS runtime foundation
Objective: create clean reusable XHS runtime modules before porting behavior.

Files:
- Create: src/social_ops_kit/platforms/xhs/browser_session.py
- Create: src/social_ops_kit/platforms/xhs/selectors.py
- Create: src/social_ops_kit/platforms/xhs/utils.py
- Create: src/social_ops_kit/platforms/xhs/client.py
- Test: tests/test_xhs_runtime_layout.py

Steps:
1. Add XhsPathSet and session config helpers.
2. Add minimal selector/timeouts container.
3. Add small generic utilities only.
4. Add tests for stable imports and path config.

---

## Phase 1B: migrate capabilities with real source

### Task 3: Douyin login lifecycle
Objective: port start_login/get_login_state/stop_login.

Source:
- /root/.hermes/scripts/mcp/douyin_mcp_server.py
- /root/.hermes/scripts/douyin/douyin_single_session.js

Destination:
- src/social_ops_kit/platforms/douyin/login.py
- src/social_ops_kit/platforms/douyin/browser.py
- src/social_ops_kit/platforms/douyin/state.py

### Task 4: Douyin publish with music
Objective: port stable publish_image_post_with_music path.

Source:
- /root/.hermes/scripts/douyin/douyin_dynamic_make_assets.js
- /root/.hermes/scripts/douyin/douyin_dynamic_publish_with_music.js
- /root/.hermes/scripts/mcp/douyin_mcp_server.py

Destination:
- src/social_ops_kit/platforms/douyin/assets.py
- src/social_ops_kit/platforms/douyin/publish.py
- src/social_ops_kit/platforms/douyin/browser.py
- src/social_ops_kit/platforms/douyin/state.py

### Task 5: Douyin recent-post inspection and comment reply
Objective: port inspect_recent_posts and reply_visible_comments.

Source:
- /root/.hermes/scripts/douyin/douyin_manage_latest_inspect.js
- /root/.hermes/scripts/douyin/douyin_reply_visible_unreplied.js
- /root/.hermes/scripts/douyin/douyin_comment_collect.js
- /root/.hermes/scripts/douyin/douyin_post_reply.js

Destination:
- src/social_ops_kit/platforms/douyin/inspect.py
- src/social_ops_kit/platforms/douyin/comments.py
- src/social_ops_kit/platforms/douyin/state.py

### Task 6: XHS search
Objective: port stable search_content path.

Source:
- /root/.hermes/mcp/xhs-mcp/node_modules/@sillyl12324/xhs-mcp/dist/xhs/clients/services/search.js
- /root/.hermes/mcp/xhs-mcp/node_modules/@sillyl12324/xhs-mcp/dist/tools/content.js

Destination:
- src/social_ops_kit/platforms/xhs/search.py
- src/social_ops_kit/platforms/xhs/client.py
- src/social_ops_kit/platforms/xhs/browser_session.py

### Task 7: XHS create_and_publish_draft
Objective: port stable one-click draft + publish path.

Source:
- /root/.hermes/mcp/xhs-mcp/node_modules/@sillyl12324/xhs-mcp/dist/tools/draft.js
- /root/.hermes/mcp/xhs-mcp/node_modules/@sillyl12324/xhs-mcp/dist/xhs/clients/services/publish.js
- /root/.hermes/mcp/xhs-mcp/node_modules/@sillyl12324/xhs-mcp/dist/core/hermes-draft-renderer.js

Destination:
- src/social_ops_kit/platforms/xhs/drafts.py
- src/social_ops_kit/platforms/xhs/client.py
- src/social_ops_kit/platforms/xhs/browser_session.py

### Task 8: XHS stats and comment reply
Objective: port get_post_stats and reply_comment from creator/comment flows.

Source:
- /root/.hermes/mcp/xhs-mcp/node_modules/@sillyl12324/xhs-mcp/dist/xhs/clients/services/creator.js
- /root/.hermes/mcp/xhs-mcp/node_modules/@sillyl12324/xhs-mcp/dist/tools/creator.js
- /root/.hermes/mcp/xhs-mcp/node_modules/@sillyl12324/xhs-mcp/dist/xhs/clients/services/interact.js

Destination:
- src/social_ops_kit/platforms/xhs/posts.py
- src/social_ops_kit/platforms/xhs/comments.py
- src/social_ops_kit/platforms/xhs/client.py

---

## Deferred from Phase 1

These capabilities are currently contract-level only because no stable execution source was found yet:

- douyin_search_content
- douyin_get_post_stats
- douyin_list_messages
- douyin_reply_message
- xhs_list_messages
- xhs_reply_message

They should stay documented but not be falsely marked as implemented until real runtime source is added.

---

## Verification commands

```bash
cd /root/social-ops-kit
python3 -m pytest -q
PYTHONPATH=src python3 -m social_ops_kit.cli manifest
```
