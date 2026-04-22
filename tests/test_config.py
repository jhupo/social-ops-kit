from social_ops_kit.config import SocialOpsConfig


def test_default_workspace_path():
    cfg = SocialOpsConfig.from_env()
    assert str(cfg.workspace).endswith('social-ops-kit')
    assert str(cfg.douyin_state_dir).endswith('state/douyin')
    assert str(cfg.xhs_state_dir).endswith('state/xhs')
