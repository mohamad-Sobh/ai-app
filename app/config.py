"""App configuration defaults with environment overrides."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class AppSettings:
    host: str = os.getenv("APP_HOST", "0.0.0.0")
    port: int = int(os.getenv("APP_PORT", "8000"))
