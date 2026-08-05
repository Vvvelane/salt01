from datetime import datetime, timezone
import unittest

from nacl_quant.contracts import ReferenceTimeKind, ReferenceTimeSpec, resolve_reference_time, ContractViolation
from nacl_quant.decisions import Decision, require_realtime_reference, validate_realtime_decision
from nacl_quant.events import Event
from nacl_quant.features import FeatureRow
from nacl_quant.labels import LabelRow


UTC = timezone.utc


def event():
    return Event(
        event_id="event-1",
        instrument_id="instrument-1",
        anchor_time=datetime(2026, 1, 1, 9, 10, tzinfo=UTC),
        emitted_at=datetime(2026, 1, 1, 9, 12, tzinfo=UTC),
        information_cutoff=datetime(2026, 1, 1, 9, 12, tzinfo=UTC),
        direction=None,
        selector_id="selector:v1",
        trading_date="2026-01-01",
    )


class ReferenceCausalityTests(unittest.TestCase):
    def test_anchor_emitted_and_custom_references_resolve_explicitly(self):
        current = event()
        anchor = resolve_reference_time(current, ReferenceTimeSpec.anchor())
        emitted = resolve_reference_time(current, ReferenceTimeSpec.emitted())
        custom_time = datetime(2026, 1, 1, 9, 13, tzinfo=UTC)
        custom = resolve_reference_time(current, ReferenceTimeSpec.custom("confirmed_close", custom_time))
        self.assertEqual(anchor.kind, ReferenceTimeKind.ANCHOR_TIME)
        self.assertEqual(anchor.reference_time, current.anchor_time)
        self.assertTrue(anchor.retrospective)
        self.assertFalse(emitted.retrospective)
        self.assertEqual(custom.custom_name, "confirmed_close")
        self.assertEqual(custom.reference_time, custom_time)

    def test_feature_label_and_execution_contracts_can_declare_custom_reference(self):
        current = event()
        reference_time = datetime(2026, 1, 1, 9, 13, tzinfo=UTC)
        feature = FeatureRow(
            event_id=current.event_id,
            feature_set_id="features:v1",
            asof_time=reference_time,
            max_input_available_at=reference_time,
            reference_time_kind=ReferenceTimeKind.CUSTOM,
            reference_time=reference_time,
            reference_name="confirmed_close",
        )
        label = LabelRow(
            event_id=current.event_id,
            label_id="label:v1",
            value=1,
            reference_time_kind=ReferenceTimeKind.CUSTOM,
            reference_time=reference_time,
            reference_name="confirmed_close",
            window_start=reference_time,
            window_end=datetime(2026, 1, 1, 9, 14, tzinfo=UTC),
            resolution_status="resolved",
            resolution_policy="close_only:v1",
        )
        self.assertEqual(feature.reference_name, label.reference_name)

    def test_real_time_decision_rejects_before_emission_and_retro_labels_are_protected(self):
        current = event()
        early = Decision(
            event_id=current.event_id,
            decision_time=datetime(2026, 1, 1, 9, 11, tzinfo=UTC),
            action=1,
            policy_id="policy:v1",
        )
        with self.assertRaises(ContractViolation):
            validate_realtime_decision(current, early)
        require_realtime_reference(current, current.emitted_at)
        with self.assertRaises(ContractViolation):
            require_realtime_reference(current, current.anchor_time)
        retrospective = Decision(
            event_id=current.event_id,
            decision_time=current.emitted_at,
            action=1,
            policy_id="policy:v1",
            retrospective=True,
        )
        with self.assertRaises(ContractViolation):
            validate_realtime_decision(current, retrospective)

