from __future__ import annotations

from social_ops_kit.platforms.base import Capability, PlatformAdapter
from .contracts import DouyinCapabilityCatalog


class DouyinAdapter(PlatformAdapter):
    platform_name = "douyin"

    def stable_capabilities(self) -> list[Capability]:
        return DouyinCapabilityCatalog.stable()
