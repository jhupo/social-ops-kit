from __future__ import annotations

from social_ops_kit.platforms.base import Capability, PlatformAdapter
from .contracts import XhsCapabilityCatalog


class XhsAdapter(PlatformAdapter):
    platform_name = "xhs"

    def stable_capabilities(self) -> list[Capability]:
        return XhsCapabilityCatalog.stable()
