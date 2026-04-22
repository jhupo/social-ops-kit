from pathlib import Path


README = Path(__file__).resolve().parents[1] / "README.md"


def test_readme_includes_tool_matrix_and_maturity_legend() -> None:
    content = README.read_text(encoding="utf-8")
    assert "## Tool matrix" in content
    assert "Maturity legend" in content
    assert "douyin_check_auth" in content
    assert "xhs_get_notifications" in content
    assert "external_dependent" in content
