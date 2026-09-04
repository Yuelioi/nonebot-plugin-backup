from pathlib import Path

from nonebot import get_plugin_config
from pydantic import BaseModel, Field, field_validator


class Config(BaseModel):
    """Plugin configuration loaded from NoneBot's environment."""

    backup_group: set[str] = Field(default_factory=set)
    backup_command: str = "备份群文件"
    recovery_command: str = "恢复群文件"
    backup_maxsize: float = 300
    backup_minsize: float = 0.01
    backup_temp_files: bool = True
    backup_temp_file_ignore: set[str] = Field(
        default_factory=lambda: {".gif", ".png", ".jpg", ".mp4"}
    )
    backup_request_timeout: float = 60
    backup_chunk_size: int = 64 * 1024

    @field_validator("backup_maxsize", "backup_minsize", "backup_request_timeout")
    @classmethod
    def validate_positive_number(cls, value: float) -> float:
        if value < 0:
            raise ValueError("must not be negative")
        return value

    @field_validator("backup_chunk_size")
    @classmethod
    def validate_chunk_size(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("must be positive")
        return value

    @field_validator("backup_temp_file_ignore", mode="before")
    @classmethod
    def normalize_suffixes(cls, value: object) -> object:
        if not isinstance(value, (list, set, tuple)):
            return value
        return {
            suffix.lower() if str(suffix).startswith(".") else f".{str(suffix).lower()}"
            for suffix in value
        }

    def allows_group(self, group_id: int) -> bool:
        return not self.backup_group or str(group_id) in self.backup_group

    def group_directory(self, data_directory: Path, group_id: int) -> Path:
        return data_directory / str(group_id)


plugin_config = get_plugin_config(Config)
