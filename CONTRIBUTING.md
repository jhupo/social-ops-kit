# Contributing

## Ground rules

1. Keep stable core small.
2. Do not merge private-path assumptions into public code.
3. Keep strategy assets in `skills/` and execution assets in `src/`.
4. Experimental platform hacks belong behind explicit experimental boundaries.
5. Add tests for every stable surface change.

## Development

```bash
cd /root/social-ops-kit
python3 -m pytest -q
PYTHONPATH=src python3 -m social_ops_kit.cli manifest
```

## Pull request checklist

- [ ] no hardcoded `/root`, `/tmp`, or local proxy assumptions in stable code
- [ ] no debug or probe scripts exposed as stable MCP tools
- [ ] docs updated if public tool surface changed
- [ ] tests pass
