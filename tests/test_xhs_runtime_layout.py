from social_ops_kit.config import SocialOpsConfig
from social_ops_kit.platforms.xhs.browser_session import XhsPathSet
from social_ops_kit.platforms.xhs.client import XhsRuntime
from social_ops_kit.platforms.xhs.utils import is_http_url


def test_xhs_path_set_defaults() -> None:
    paths = XhsPathSet.from_config(SocialOpsConfig.from_env())
    assert str(paths.drafts_dir).endswith("state/xhs/drafts")
    assert str(paths.profile_dir).endswith("state/xhs/profile")


def test_xhs_runtime_builds_from_config() -> None:
    runtime = XhsRuntime.from_config(SocialOpsConfig.from_env())
    assert runtime.browser.locale == "zh-CN"
    assert is_http_url("https://example.com/image.png")
    assert not is_http_url("/tmp/file.png")
