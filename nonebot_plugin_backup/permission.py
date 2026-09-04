from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER, Permission


def build_permission(level: int) -> Permission:
    """Build the command permission for the configured access level."""
    if level == 1:
        return SUPERUSER
    if level == 2:
        return SUPERUSER | GROUP_ADMIN | GROUP_OWNER
    return Permission()
