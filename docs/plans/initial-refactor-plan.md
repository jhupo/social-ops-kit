# social-ops-kit Initial Refactor Plan

> For Hermes: use subagent-driven-development for future execution task-by-task.

Goal: turn the private working set into a clean open-source skill + MCP foundation without dragging debug sprawl into the public core.

Architecture: keep stable platform operations in MCP-facing adapters and keep content/review logic in skills. Port only the stable curated surface first; everything else becomes optional or experimental later.

Tech stack: Python 3.11 for package structure and MCP-facing surface; Markdown skills for strategy assets.

---

## Task buckets

1. Scaffold package and docs
2. Curate stable tool surface
3. Port Douyin adapter flows
4. Port XHS adapter flows
5. Add real MCP runtime
6. Add tests and fixtures
7. Add packaging / CI
