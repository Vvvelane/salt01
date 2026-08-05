"""Lazy, explicit adapters for the audited current CSV market data."""

from .adapter import AdapterError, CsvMarketDataAdapter
from .catalog import CatalogEntry, CatalogError, CatalogQuery, DataCatalog
from .config import (
    AdapterConfig,
    DatasetFamily,
    DatasetIdentity,
    FieldSemantics,
    IntervalSpec,
    PendingConfigurationError,
    TimestampConfig,
    TimestampRole,
)
from .loader import CsvLoadError, CsvLoader, CsvRow
from .session import (
    ConfiguredSessionResolver,
    SessionDefinition,
    SessionResolution,
    SessionResolutionError,
    SessionResolver,
)
from .validation import CsvValidator, ValidationIssue, ValidationReport

__all__ = [
    "AdapterConfig",
    "AdapterError",
    "CatalogEntry",
    "CatalogError",
    "CatalogQuery",
    "ConfiguredSessionResolver",
    "CsvLoadError",
    "CsvLoader",
    "CsvMarketDataAdapter",
    "CsvRow",
    "CsvValidator",
    "DataCatalog",
    "DatasetFamily",
    "DatasetIdentity",
    "FieldSemantics",
    "IntervalSpec",
    "PendingConfigurationError",
    "SessionDefinition",
    "SessionResolution",
    "SessionResolutionError",
    "SessionResolver",
    "TimestampConfig",
    "TimestampRole",
    "ValidationIssue",
    "ValidationReport",
]
