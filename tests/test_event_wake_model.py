from dataclasses import dataclass, field


@dataclass
class EventLedger:
    authority_epoch: int
    generation: int
    processed: set[str] = field(default_factory=set)
    outstanding_generation: int | None = None

    def observe(self, event_id: str, generation: int, expected_epoch: int) -> str:
        if event_id in self.processed:
            return "DUPLICATE_NO_REPLAY"
        if expected_epoch != self.authority_epoch:
            return "EPOCH_MISMATCH_REJECT"
        if generation < self.generation:
            return "STALE_GENERATION_REJECT"
        if generation > self.generation + 1:
            return "GENERATION_AHEAD_REJECT"
        self.processed.add(event_id)
        if generation == self.generation + 1:
            self.generation = generation
            self.outstanding_generation = None
            return "NEXT_GENERATION_ACCEPTED"
        return "CURRENT_GENERATION_OBSERVED"

    def emit_next(self, owner_epoch: int, meaningful_checkpoint: bool) -> int:
        if owner_epoch != self.authority_epoch:
            raise ValueError("only current authority may emit")
        if not meaningful_checkpoint:
            raise ValueError("heartbeat-only event forbidden")
        if self.outstanding_generation is not None:
            raise ValueError("only one outstanding continuation generation")
        self.outstanding_generation = self.generation + 1
        return self.outstanding_generation


def test_duplicate_event_is_harmless():
    s = EventLedger(authority_epoch=17, generation=4)
    assert s.observe("e-1", 4, 17) == "CURRENT_GENERATION_OBSERVED"
    assert s.observe("e-1", 4, 17) == "DUPLICATE_NO_REPLAY"


def test_generation_cannot_jump():
    s = EventLedger(authority_epoch=17, generation=4)
    assert s.observe("e-2", 6, 17) == "GENERATION_AHEAD_REJECT"


def test_stale_authority_cannot_emit():
    s = EventLedger(authority_epoch=17, generation=4)
    try:
        s.emit_next(16, True)
        assert False, "expected rejection"
    except ValueError:
        pass


def test_heartbeat_cannot_emit():
    s = EventLedger(authority_epoch=17, generation=4)
    try:
        s.emit_next(17, False)
        assert False, "expected rejection"
    except ValueError:
        pass


def test_only_one_generation_outstanding():
    s = EventLedger(authority_epoch=17, generation=4)
    assert s.emit_next(17, True) == 5
    try:
        s.emit_next(17, True)
        assert False, "expected rejection"
    except ValueError:
        pass
    assert s.observe("e-5", 5, 17) == "NEXT_GENERATION_ACCEPTED"
    assert s.emit_next(17, True) == 6


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
