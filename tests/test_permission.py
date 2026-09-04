import pytest
from pydantic import ValidationError

from nonebot_plugin_backup.config import Config
from nonebot_plugin_backup.permission import build_permission


def test_permission_levels_have_expected_checkers() -> None:
    assert len(build_permission(1).checkers) == 1
    assert len(build_permission(2).checkers) == 3
    assert len(build_permission(3).checkers) == 0


@pytest.mark.parametrize("level", [0, 4])
def test_config_rejects_unknown_permission_level(level: int) -> None:
    with pytest.raises(ValidationError):
        Config(backup_permission=level)  # type: ignore[arg-type]
