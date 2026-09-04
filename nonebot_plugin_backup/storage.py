import asyncio
import re
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import aiofiles
import aiohttp
from nonebot import logger
from nonebot.adapters.onebot.v11 import Bot

from .config import Config
from .models import BackupReport, RestoreReport

_INVALID_PATH_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def safe_name(name: str, fallback: str) -> str:
    """Turn an untrusted QQ filename into one safe local path segment."""
    cleaned = _INVALID_PATH_CHARS.sub("_", name).strip().rstrip(".")
    return cleaned if cleaned not in {"", ".", ".."} else fallback


class BackupStorage:
    """Hide OneBot traversal, HTTP streaming and persistence behind two operations."""

    def __init__(self, data_directory: Path, config: Config) -> None:
        self._data_directory = data_directory
        self._config = config
        self._locks: dict[int, asyncio.Lock] = {}

    @asynccontextmanager
    async def _operation(self, group_id: int) -> AsyncIterator[None]:
        lock = self._locks.setdefault(group_id, asyncio.Lock())
        async with lock:
            yield

    async def backup(self, bot: Bot, group_id: int) -> BackupReport:
        async with self._operation(group_id):
            report = BackupReport()
            root_dir = self._config.group_directory(self._data_directory, group_id)
            root = await bot.get_group_root_files(group_id=group_id)
            if self._config.backup_temp_files:
                await self._download_files(bot, group_id, root.get("files") or [], root_dir, report)

            for folder in root.get("folders") or []:
                folder_id = str(folder["folder_id"])
                folder_name = safe_name(str(folder["folder_name"]), folder_id)
                content = await bot.get_group_files_by_folder(
                    group_id=group_id, folder_id=folder_id
                )
                await self._download_files(
                    bot, group_id, content.get("files") or [], root_dir / folder_name, report
                )
            return report

    async def restore(self, bot: Bot, group_id: int) -> RestoreReport:
        async with self._operation(group_id):
            report = RestoreReport()
            root_dir = self._config.group_directory(self._data_directory, group_id)
            if not root_dir.is_dir():
                raise FileNotFoundError(f"没有找到群 {group_id} 的备份目录")

            root = await bot.get_group_root_files(group_id=group_id)
            await self._upload_files(bot, group_id, "/", root_dir, root.get("files") or [], report)
            remote_folders = {
                str(folder["folder_name"]): str(folder["folder_id"])
                for folder in root.get("folders") or []
            }
            for directory in sorted(path for path in root_dir.iterdir() if path.is_dir()):
                folder_id = remote_folders.get(directory.name)
                if folder_id is None:
                    await bot.create_group_file_folder(
                        group_id=group_id, name=directory.name, parent_id="/"
                    )
                    refreshed = await bot.get_group_root_files(group_id=group_id)
                    folder_id = next(
                        str(item["folder_id"])
                        for item in refreshed.get("folders") or []
                        if str(item["folder_name"]) == directory.name
                    )
                content = await bot.get_group_files_by_folder(
                    group_id=group_id, folder_id=folder_id
                )
                await self._upload_files(
                    bot, group_id, folder_id, directory, content.get("files") or [], report
                )
            return report

    async def _download_files(
        self,
        bot: Bot,
        group_id: int,
        files: list[dict[str, Any]],
        directory: Path,
        report: BackupReport,
    ) -> None:
        timeout = aiohttp.ClientTimeout(total=self._config.backup_request_timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for item in files:
                await self._download_file(session, bot, group_id, item, directory, report)

    async def _download_file(
        self,
        session: aiohttp.ClientSession,
        bot: Bot,
        group_id: int,
        item: dict[str, Any],
        directory: Path,
        report: BackupReport,
    ) -> None:
        remote_name = str(item["file_name"])
        file_name = safe_name(remote_name, str(item["file_id"]))
        size = int(item.get("file_size", 0))
        relative_name = str((directory / file_name).relative_to(self._data_directory))
        size_mb = size / 1024 / 1024
        if size_mb < self._config.backup_minsize:
            return
        if size_mb > self._config.backup_maxsize:
            report.too_large.append(relative_name)
            return
        if directory == self._config.group_directory(self._data_directory, group_id):
            if Path(file_name).suffix.lower() in self._config.backup_temp_file_ignore:
                return

        target = directory / file_name
        if target.is_file() and target.stat().st_size == size:
            report.skipped += 1
            report.bytes_total += size
            return

        temporary = target.with_name(f".{target.name}.part")
        try:
            info = await bot.get_group_file_url(
                group_id=group_id,
                file_id=str(item["file_id"]),
                busid=int(item["busid"]),
            )
            directory.mkdir(parents=True, exist_ok=True)
            async with session.get(str(info["url"])) as response:
                response.raise_for_status()
                async with aiofiles.open(temporary, "wb") as output:
                    async for chunk in response.content.iter_chunked(
                        self._config.backup_chunk_size
                    ):
                        await output.write(chunk)
            temporary.replace(target)
            report.downloaded += 1
            report.bytes_total += target.stat().st_size
        except (aiohttp.ClientError, OSError, KeyError, ValueError) as error:
            temporary.unlink(missing_ok=True)
            report.failed.append(relative_name)
            logger.warning(f"群文件下载失败 {relative_name}: {error}")

    async def _upload_files(
        self,
        bot: Bot,
        group_id: int,
        folder_id: str,
        directory: Path,
        remote_files: list[dict[str, Any]],
        report: RestoreReport,
    ) -> None:
        existing = {str(item["file_name"]) for item in remote_files}
        for path in sorted(item for item in directory.iterdir() if item.is_file()):
            if path.name in existing:
                report.skipped += 1
                continue
            try:
                await bot.upload_group_file(
                    group_id=group_id,
                    file=str(path.resolve()),
                    name=path.name,
                    folder=folder_id,
                )
                report.uploaded += 1
            except Exception as error:  # OneBot implementations expose heterogeneous errors.
                report.failed.append(str(path.relative_to(self._data_directory)))
                logger.warning(f"群文件上传失败 {path}: {error}")
