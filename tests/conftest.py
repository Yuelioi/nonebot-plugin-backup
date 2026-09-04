import nonebot

nonebot.init(driver="~none")
assert nonebot.load_plugin("nonebot_plugin_backup") is not None
