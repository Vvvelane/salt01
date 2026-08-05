"""On-demand cataloging of the existing CSV tree; no data rows are loaded."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import DatasetFamily


class CatalogError(ValueError):
    pass


@dataclass(frozen=True)
class CatalogQuery:
    family: DatasetFamily | None = None
    interval: str | None = None
    exchange: str | None = None
    instrument: str | None = None
    filename: str | None = None


@dataclass(frozen=True)
class CatalogEntry:
    path: Path
    relative_path: str
    family: DatasetFamily
    interval: str | None
    exchange: str | None
    instrument: str | None
    filename: str

    @property
    def source_id(self) -> str:
        """Stable source identity relative to the configured market-data root."""

        return self.relative_path


class DataCatalog:
    """A lazy path catalog. Construction and import perform no directory scan."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).expanduser().resolve()

    def list(self, query: CatalogQuery | None = None) -> tuple[CatalogEntry, ...]:
        if not self.root.is_dir():
            raise CatalogError(f"market-data root is not a directory: {self.root}")
        query = query or CatalogQuery()
        entries = []
        for path in self.root.rglob("*.csv"):
            if not path.is_file():
                continue
            entry = self._entry(path)
            if self._matches(entry, query):
                entries.append(entry)
        return tuple(sorted(entries, key=lambda item: item.relative_path))

    def get(self, relative_path: str) -> CatalogEntry:
        candidate = (self.root / relative_path).resolve()
        self._ensure_within_root(candidate)
        if not candidate.is_file() or candidate.suffix.lower() != ".csv":
            raise CatalogError(f"CSV file not found: {relative_path}")
        return self._entry(candidate)

    def _entry(self, path: Path) -> CatalogEntry:
        relative = path.relative_to(self.root)
        parts = relative.parts
        if parts and parts[0] == "主要合约" and len(parts) >= 5:
            return CatalogEntry(
                path=path,
                relative_path=relative.as_posix(),
                family=DatasetFamily.MAJOR_CONTINUOUS,
                interval=parts[1],
                exchange=parts[2],
                instrument=parts[3],
                filename=path.name,
            )
        if parts and parts[0] == "主要合约" and len(parts) == 3:
            exchange, instrument = self._split_filename_identity(path.stem)
            return CatalogEntry(
                path=path,
                relative_path=relative.as_posix(),
                family=DatasetFamily.MAJOR_CONTINUOUS,
                interval=parts[1],
                exchange=exchange,
                instrument=instrument,
                filename=path.name,
            )
        if parts and parts[0] == "全部合约" and len(parts) >= 5:
            return CatalogEntry(
                path=path,
                relative_path=relative.as_posix(),
                family=DatasetFamily.SINGLE_CONTRACT,
                interval=parts[1],
                exchange=parts[2],
                instrument=parts[3],
                filename=path.name,
            )
        if parts and parts[0] == "全部合约" and len(parts) == 4:
            exchange, filename_instrument = self._split_filename_identity(path.stem)
            return CatalogEntry(
                path=path,
                relative_path=relative.as_posix(),
                family=DatasetFamily.SINGLE_CONTRACT,
                interval=parts[1],
                exchange=exchange,
                instrument=parts[2] or filename_instrument,
                filename=path.name,
            )
        if parts and parts[0] == "IM指数数据":
            interval = "日" if path.stem.endswith("-daily") else None
            return CatalogEntry(
                path=path,
                relative_path=relative.as_posix(),
                family=DatasetFamily.INDEX,
                interval=interval,
                exchange=None,
                instrument=path.stem.removesuffix("-daily"),
                filename=path.name,
            )
        raise CatalogError(f"unrecognized CSV layout: {relative.as_posix()}")

    @staticmethod
    def _split_filename_identity(stem: str) -> tuple[str | None, str | None]:
        if "." not in stem:
            return None, None
        exchange, instrument = stem.split(".", 1)
        return exchange or None, instrument or None

    @staticmethod
    def _matches(entry: CatalogEntry, query: CatalogQuery) -> bool:
        return all(
            value is None or actual == value
            for actual, value in (
                (entry.family, query.family),
                (entry.interval, query.interval),
                (entry.exchange, query.exchange),
                (entry.instrument, query.instrument),
                (entry.filename, query.filename),
            )
        )

    def _ensure_within_root(self, path: Path) -> None:
        try:
            path.relative_to(self.root)
        except ValueError as exc:
            raise CatalogError("path escapes configured market-data root") from exc
