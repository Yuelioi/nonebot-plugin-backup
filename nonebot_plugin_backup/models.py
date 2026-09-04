from dataclasses import dataclass, field


@dataclass(slots=True)
class BackupReport:
    downloaded: int = 0
    skipped: int = 0
    bytes_total: int = 0
    too_large: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)

    def render(self, elapsed: float, max_size_mb: float) -> str:
        too_large = "\n".join(self.too_large) or "无"
        failed_names = "\n".join(self.failed)
        failed = f"\n检测到下载失败文件:\n{failed_names}" if self.failed else ""
        return (
            f"备份完成，耗时 {elapsed:.2f} 秒；下载 {self.downloaded} 个，"
            f"跳过已有 {self.skipped} 个，累计 {self.bytes_total / 1024 / 1024:.2f} MiB。\n"
            f"未备份的大文件（>{max_size_mb:g} MiB）：\n{too_large}{failed}"
        )


@dataclass(slots=True)
class RestoreReport:
    uploaded: int = 0
    skipped: int = 0
    failed: list[str] = field(default_factory=list)

    def render(self) -> str:
        failed_names = "\n".join(self.failed)
        failed = f"\n上传失败：\n{failed_names}" if self.failed else ""
        return f"恢复完成；上传 {self.uploaded} 个，跳过群内已有 {self.skipped} 个。{failed}"
