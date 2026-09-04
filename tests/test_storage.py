from pathlib import Path
from unittest.mock import AsyncMock

from aiohttp import web

from nonebot_plugin_backup.config import Config
from nonebot_plugin_backup.storage import BackupStorage, safe_name


async def serve_file(content: bytes) -> tuple[web.AppRunner, str]:
    async def handle_file(_: web.Request) -> web.Response:
        return web.Response(body=content)

    app = web.Application()
    app.router.add_get("/file", handle_file)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    sockets = site._server.sockets  # type: ignore[union-attr]
    port = sockets[0].getsockname()[1]
    return runner, f"http://127.0.0.1:{port}/file"


def test_safe_name_blocks_path_traversal() -> None:
    assert safe_name("../secret?.txt", "id") == ".._secret_.txt"
    assert safe_name("..", "id") == "id"


async def test_backup_streams_file_and_skips_existing(tmp_path: Path) -> None:
    content = b"group file contents"
    runner, url = await serve_file(content)
    bot = AsyncMock()
    item = {
        "file_id": "file-1",
        "file_name": "notes.txt",
        "file_size": len(content),
        "busid": 1,
    }
    bot.get_group_root_files.return_value = {"files": [item], "folders": []}
    bot.get_group_file_url.return_value = {"url": url}
    storage = BackupStorage(tmp_path, Config(backup_minsize=0))

    try:
        first = await storage.backup(bot, 123)
        second = await storage.backup(bot, 123)
    finally:
        await runner.cleanup()

    assert (tmp_path / "123" / "notes.txt").read_bytes() == content
    assert (first.downloaded, first.skipped) == (1, 0)
    assert (second.downloaded, second.skipped) == (0, 1)


async def test_restore_creates_folder_and_uploads_files(tmp_path: Path) -> None:
    group_dir = tmp_path / "123"
    folder = group_dir / "documents"
    folder.mkdir(parents=True)
    (group_dir / "root.txt").write_text("root", encoding="utf-8")
    (folder / "inside.txt").write_text("inside", encoding="utf-8")

    bot = AsyncMock()
    bot.get_group_root_files.side_effect = [
        {"files": [], "folders": []},
        {"files": [], "folders": [{"folder_name": "documents", "folder_id": "folder-1"}]},
    ]
    bot.get_group_files_by_folder.return_value = {"files": []}
    report = await BackupStorage(tmp_path, Config()).restore(bot, 123)

    assert report.uploaded == 2
    bot.create_group_file_folder.assert_awaited_once_with(
        group_id=123, name="documents", parent_id="/"
    )
    assert bot.upload_group_file.await_count == 2
