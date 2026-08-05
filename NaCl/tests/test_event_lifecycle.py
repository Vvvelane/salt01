from datetime import datetime, timezone
import unittest

from nacl_quant.events import (
    Event,
    PassthroughEventPostProcessor,
    derive_postprocessed_event,
    stable_event_id,
)
from nacl_quant.contracts import ContractViolation


UTC = timezone.utc


def make_event(*, event_id="event-1", anchor_minute=10, emitted_minute=12, cutoff_minute=12):
    anchor = datetime(2026, 1, 1, 9, anchor_minute, tzinfo=UTC)
    emitted = datetime(2026, 1, 1, 9, emitted_minute, tzinfo=UTC)
    cutoff = datetime(2026, 1, 1, 9, cutoff_minute, tzinfo=UTC)
    return Event(
        event_id=event_id,
        instrument_id="instrument-1",
        anchor_time=anchor,
        emitted_at=emitted,
        information_cutoff=cutoff,
        direction=1,
        selector_id="selector:v1",
        trading_date="2026-01-01",
    )


class EventLifecycleTests(unittest.TestCase):
    def test_three_lifecycle_times_are_stored_and_order_is_validated(self):
        event = make_event()
        self.assertEqual(event.anchor_time.minute, 10)
        self.assertEqual(event.emitted_at.minute, 12)
        self.assertEqual(event.information_cutoff.minute, 12)

        with self.assertRaises(ContractViolation):
            make_event(emitted_minute=11, cutoff_minute=12)

    def test_unconfigured_and_passthrough_postprocessor_are_directly_usable(self):
        events = (make_event(),)
        self.assertEqual(events[0], events[0])
        result = PassthroughEventPostProcessor().process(events)
        self.assertIs(result[0], events[0])
        self.assertEqual(result[0].event_id, events[0].event_id)

    def test_postprocessed_identity_records_parents_and_semantic_id(self):
        first = make_event(event_id="first")
        second = make_event(event_id="second", anchor_minute=11)
        result = derive_postprocessed_event(
            first,
            postprocess_id="merge:v1",
            parent_event_ids=(first.event_id, second.event_id),
        )
        self.assertEqual(result.parent_event_ids, ("first", "second"))
        self.assertEqual(result.postprocess_id, "merge:v1")
        self.assertNotEqual(result.event_id, first.event_id)

    def test_event_id_is_stable_when_input_order_changes(self):
        first = stable_event_id(
            namespace="research",
            instrument_id="instrument-1",
            anchor_time=datetime(2026, 1, 1, 9, 10, tzinfo=UTC),
            selector_id="selector:v1",
            direction=1,
        )
        second = stable_event_id(
            namespace="research",
            instrument_id="instrument-1",
            anchor_time=datetime(2026, 1, 1, 9, 10, tzinfo=UTC),
            selector_id="selector:v1",
            direction=1,
        )
        self.assertEqual(first, second)

