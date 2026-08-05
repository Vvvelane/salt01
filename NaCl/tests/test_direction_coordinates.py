from datetime import datetime, timezone
import unittest

from nacl_quant.contracts import ContractViolation, CoordinateState, DirectionTransform
from nacl_quant.datasets import DatasetBuilder
from nacl_quant.events import Event
from nacl_quant.features import FeatureField, FeatureRow, FeatureSchema
from nacl_quant.labels import LabelField, LabelRow, LabelSchema
from nacl_quant.contracts import ReferenceTimeKind


UTC = timezone.utc


def make_event(event_id="event-1"):
    timestamp = datetime(2026, 1, 1, 9, 10, tzinfo=UTC)
    return Event(
        event_id=event_id,
        instrument_id="instrument-1",
        anchor_time=timestamp,
        emitted_at=timestamp,
        information_cutoff=timestamp,
        direction=-1,
        selector_id="selector:v1",
        trading_date="2026-01-01",
    )


class DirectionCoordinateTests(unittest.TestCase):
    def test_single_raw_signed_transform_records_local_provenance(self):
        transform = DirectionTransform("direction:v1")
        result = transform.apply(
            event_id="event-1",
            value_event_id="event-1",
            direction=-1,
            field_name="return",
            coordinate_state=CoordinateState.RAW_SIGNED,
            value=-2.5,
        )
        self.assertEqual(result.value, 2.5)
        self.assertEqual(result.coordinate_state, CoordinateState.EVENT_ALIGNED)
        self.assertEqual(result.event_id, "event-1")
        self.assertEqual(result.direction_transform_id, "direction:v1")

    def test_invalid_repeated_unsigned_empty_direction_and_mismatched_id_fail(self):
        transform = DirectionTransform("direction:v1")
        common = dict(event_id="event-1", value_event_id="event-1", field_name="x", value=1.0)
        with self.assertRaises(ContractViolation):
            transform.apply(**common, direction=1, coordinate_state=CoordinateState.EVENT_ALIGNED)
        with self.assertRaises(ContractViolation):
            transform.apply(**common, direction=1, coordinate_state=CoordinateState.UNSIGNED)
        with self.assertRaises(ContractViolation):
            transform.apply(**common, direction=None, coordinate_state=CoordinateState.RAW_SIGNED)
        with self.assertRaises(ContractViolation):
            transform.apply(
                **{**common, "value_event_id": "other-event"},
                direction=1,
                coordinate_state=CoordinateState.RAW_SIGNED,
            )

    def test_feature_and_label_transform_independently_and_dataset_does_not_transform(self):
        event = make_event()
        transform = DirectionTransform("direction:v1")
        feature_aligned = transform.apply(
            event_id=event.event_id,
            value_event_id=event.event_id,
            direction=event.direction,
            field_name="feature_return",
            coordinate_state=CoordinateState.RAW_SIGNED,
            value=3.0,
        )
        label_aligned = transform.apply(
            event_id=event.event_id,
            value_event_id=event.event_id,
            direction=event.direction,
            field_name="future_return",
            coordinate_state=CoordinateState.RAW_SIGNED,
            value=4.0,
        )
        self.assertEqual(feature_aligned.value, -3.0)
        self.assertEqual(label_aligned.value, -4.0)

        feature_schema = FeatureSchema("features:v1", (FeatureField("feature_return", CoordinateState.RAW_SIGNED),))
        label_schema = LabelSchema("label:v1", (LabelField("future_return", CoordinateState.RAW_SIGNED),))
        feature_row = FeatureRow(
            event_id=event.event_id,
            feature_set_id="features:v1",
            asof_time=event.emitted_at,
            max_input_available_at=event.emitted_at,
            reference_time_kind=ReferenceTimeKind.EMITTED_AT,
            reference_time=event.emitted_at,
            values={"feature_return": 3.0},
        )
        label_row = LabelRow(
            event_id=event.event_id,
            label_id="label:v1",
            value=4.0,
            reference_time_kind=ReferenceTimeKind.EMITTED_AT,
            reference_time=event.emitted_at,
            window_start=event.emitted_at,
            window_end=datetime(2026, 1, 1, 9, 11, tzinfo=UTC),
            resolution_status="resolved",
            resolution_policy="close_only:v1",
        )
        dataset = DatasetBuilder(feature_schema, label_schema).build((event,), (feature_row,), (label_row,))
        self.assertEqual(dataset.feature_rows[0].values["feature_return"], 3.0)
        self.assertEqual(dataset.label_rows[0].value, 4.0)

