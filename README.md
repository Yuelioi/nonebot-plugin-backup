<div align="center">

# NoneBot Plugin Backup

异步备份与恢复 OneBot V11 QQ 群文件。

</div>

## 功能

- 备份群文件根目录以及群文件夹内的文件；
- 按文件大小过滤，并可忽略根目录中的指定后缀；
- 已存在且大小相同的文件不会重复下载；
- 将本地备份恢复至原群或迁移至新群；
- 使用 `aiohttp` 流式下载，不阻塞事件循环，也不会把大文件一次性读入内存；
- 每个群的任务串行执行，避免并发命令破坏同一份备份。

本插件仅支持 `nonebot-adapter-onebot` 的 OneBot V11。实际可用性取决于协议实现端是否实现群文件相关动作；恢复文件及创建文件夹通常要求机器人具有群管理员权限。

## 安装

使用 NB-CLI（商店推荐方式）：

```shell
nb plugin install nonebot-plugin-backup
```

使用 uv：

```shell
uv add nonebot-plugin-backup
```

然后按 NoneBot 的插件加载方式加载 `nonebot_plugin_backup`。

## 配置

所有配置均为可选项，插件可以零配置加载。可在 NoneBot 的 `.env` 或 `.env.*` 中设置：

| 配置项 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `backup_group` | `set[str]` | `set()` | 允许使用插件的群号；空集合允许所有群 |
| `backup_command` | `str` | `备份群文件` | 备份命令 |
| `recovery_command` | `str` | `恢复群文件` | 恢复命令 |
| `backup_maxsize` | `float` | `300` | 单文件上限，单位 MiB |
| `backup_minsize` | `float` | `0.01` | 单文件下限，单位 MiB |
| `backup_temp_files` | `bool` | `true` | 是否备份群文件根目录中的临时文件 |
| `backup_temp_file_ignore` | `set[str]` | `{.gif,.png,.jpg,.mp4}` | 根目录忽略的文件后缀，不区分大小写 |
| `backup_request_timeout` | `float` | `60` | 单次下载总超时，单位秒 |
| `backup_chunk_size` | `int` | `65536` | 流式下载块大小，单位字节 |

示例：

```dotenv
BACKUP_GROUP=["123456789"]
BACKUP_MAXSIZE=500
BACKUP_TEMP_FILE_IGNORE=[".gif", ".png", ".jpg", ".mp4"]
```

## 使用

在允许的群中发送 `备份群文件` 即可备份。发送 `恢复群文件` 会将该群对应的数据上传回群文件。

数据目录由 `nonebot-plugin-localstore` 管理，不再依赖机器人进程的当前工作目录。迁移到新群时，先找到 localstore 分配给本插件的数据目录，再将旧群号目录复制并改名为新群号。

下载采用临时 `.part` 文件并在成功后原子替换目标文件。下载失败不会留下看似完整的文件；恢复时同名远端文件会被跳过，不会覆盖。

## 开发

```shell
uv sync --all-groups
uv run ruff format .
uv run ruff check .
uv run pytest
uv build
```

当前发布规范核查见 [`docs/nonebot-plugin-publishing-research.md`](docs/nonebot-plugin-publishing-research.md)。

## 许可证

[GPL-3.0](LICENSE)
