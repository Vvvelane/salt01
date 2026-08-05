"""Explicit, event-ID based offline dataset assembly."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Protocol, Sequence

from .contracts import ContractViolation, CoordinateState
from .events import Event
from .features import FeatureRow, FeatureSchema
from .labels import LabelRow, LabelSchema


@dataclass(frozen=True)
class TrainingDataset:
    events: tuple[Event, ...]
    feature_rows: tuple[FeatureRow, ...]
    label_rows: tuple[LabelRow, ...]
    feature_schema: FeatureSchema
    label_schema: LabelSchema

    @property
    def event_ids(self) -> frozenset[str]:
        return frozenset(event.event_id for event in self.events)


class TemporalSplitter(Protocol):
    """Contract for later project-specific time-group/purge/embargo splitters."""

    def split(self, dataset: TrainingDataset, rules: object) -> Mapping[str, frozenset[str]]: ...


class DatasetBuilder:
    """Join rows by stable event_id and validate; never performs direction transforms."""

    def __init__(self, feature_schema: FeatureSchema, label_schema: LabelSchema) -> None:
        self.feature_schema = feature_schema
        self.label_schema = label_schema

    def build(
        self,
        events: Iterable[Event],
        feature_rows: Iterable[FeatureRow],
        label_rows: Iterable[LabelRow],
    ) -> TrainingDataset:
        event_items = tuple(events)
        feature_items = tuple(feature_rows)
        label_items = tuple(label_rows)
        event_ids = [event.event_id for event in event_items]
        if len(event_ids) != len(set(event_ids)):
            raise ContractViolation("Event IDs must be unique in a dataset")
        expected = set(event_ids)
        self._validate_rows(feature_items, expected, self.feature_schema.feature_set_id, "feature")
        self._validate_rows(label_items, expected, self.label_schema.label_id, "label")
        if {row.event_id for row in feature_items} != expected:
            raise ContractViolation("Feature rows must align one-to-one by event_id")
        if {row.event_id for row in label_items} != expected:
            raise ContractViolation("Label rows must align one-to-one by event_id")
        return TrainingDataset(event_items, feature_items, label_items, self.feature_schema, self.label_schema)

    @staticmethod
    def _validate_rows(rows: Sequence[FeatureRow] | Sequence[LabelRow], expected: set[str], expected_id: str, kind: str) -> None:
        ids = [row.event_id for row in rows]
        if len(ids) != len(set(ids)):
            raise ContractViolation(f"{kind} rows must have unique event_id values")
        for row in rows:
            actual_id = row.feature_set_id if isinstance(row, FeatureRow) else row.label_id
            if actual_id != expected_id:
                raise ContractViolation(f"{kind} row uses an unexpected schema ID")
            if row.event_id not in expected:
                raise ContractViolation(f"{kind} row references an unknown event_id")
