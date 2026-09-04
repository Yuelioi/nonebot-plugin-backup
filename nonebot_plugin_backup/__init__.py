from time import monotonic

from nonebot import on_command, require
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.plugin import PluginMetadata

from .config import Config, plugin_config
from .permission import build_permission

require("nonebot_plugin_localstore")
import nonebot_plugin_localstore as localstore  # noqa: E402

from .storage import BackupStorage  # noqa: E402

__plugin_meta__ = PluginMetadata(
    name="QQ群文件备份",
    description="异步备份 QQ 群文件到本地，并可将备份恢复到群文件",
    usage="在群内发送“备份群文件”或“恢复群文件”；命令与范围可通过环境变量配置。",
    type="application",
    homepage="https://github.com/Yuelioi/nonebot-plugin-backup",
    config=Config,
    supported_adapters={"~onebot.v11"},
)

operation_permission = build_permission(plugin_config.backup_permission)
backup_matcher = on_command(
    plugin_config.backup_command,
    permission=operation_permission,
    priority=10,
    block=True,
)
restore_matcher = on_command(
    plugin_config.recovery_command,
    permission=operation_permission,
    priority=10,
    block=True,
)
storage = BackupStorage(localstore.get_plugin_data_dir(), plugin_config)


@backup_matcher.handle()
async def handle_backup(bot: Bot, event: GroupMessageEvent) -> None:
    group_id = event.group_id
    if not plugin_config.allows_group(group_id):
        await backup_matcher.finish("本群未启用群文件备份。")

    await backup_matcher.send("正在备份群文件，请稍候……")
    started = monotonic()
    report = await storage.backup(bot, group_id)
    await backup_matcher.finish(report.render(monotonic() - started, plugin_config.backup_maxsize))


@restore_matcher.handle()
async def handle_restore(bot: Bot, event: GroupMessageEvent) -> None:
    group_id = event.group_id
    if not plugin_config.allows_group(group_id):
        await restore_matcher.finish("本群未启用群文件恢复。")

    await restore_matcher.send("正在恢复群文件，请稍候（机器人需要群管理员权限）……")
    try:
        report = await storage.restore(bot, group_id)
    except FileNotFoundError as error:
        await restore_matcher.finish(str(error))
        return
    await restore_matcher.finish(report.render())
