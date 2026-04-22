from __future__ import annotations

import argparse
import json
from pathlib import Path

from social_ops_kit.config import SocialOpsConfig
from social_ops_kit.mcp.server import build_server_blueprint


SKILL_DIR = Path(__file__).resolve().parents[2] / "skills"


def _cmd_manifest() -> int:
    blueprint = build_server_blueprint()
    print(json.dumps({
        "name": blueprint.name,
        "version": blueprint.version,
        "instructions": blueprint.instructions,
        "tools": blueprint.tools,
    }, ensure_ascii=False, indent=2))
    return 0



def _cmd_skills() -> int:
    skills = []
    if SKILL_DIR.exists():
        for path in sorted(SKILL_DIR.glob("*/SKILL.md")):
            skills.append({"name": path.parent.name, "path": str(path)})
    print(json.dumps(skills, ensure_ascii=False, indent=2))
    return 0



def _cmd_doctor() -> int:
    print(json.dumps(SocialOpsConfig.from_env().doctor(), ensure_ascii=False, indent=2))
    return 0



def main() -> int:
    parser = argparse.ArgumentParser(prog="social-ops-kit")
    parser.add_argument("command", choices=["manifest", "skills", "doctor"])
    args = parser.parse_args()
    if args.command == "manifest":
        return _cmd_manifest()
    if args.command == "skills":
        return _cmd_skills()
    return _cmd_doctor()


if __name__ == "__main__":
    raise SystemExit(main())
