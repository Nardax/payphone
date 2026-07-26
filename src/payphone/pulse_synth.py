"""Synthetic rotary pulse train generation.

Produces the contact edges a real rotary dial would produce, so the decoder can
be exercised **without a payphone attached**. The same generator drives:

* unit tests (fed straight into :class:`~payphone.dial_decoder.RotaryDialDecoder`), and
* the GPIO loopback rig (replayed onto a real output pin — see ``tools/gpio_loopback.py``),

which means the bench test and the unit test cover the same waveforms.

Timing model (North American dial):
    * 10 pulses per second nominal -> 100ms per pulse cycle
    * ~61% break (open) / ~39% make (closed)
    * digit 0 is sent as **ten** pulses
"""

from __future__ import annotations

import random
from typing import List, Optional, Sequence, Tuple

Edge = Tuple[float, bool]  # (t_ms, closed)

DEFAULT_PPS = 10.0
DEFAULT_BREAK_RATIO = 0.61
DEFAULT_INTERDIGIT_MS = 600.0


def digit_to_pulses(digit: int) -> int:
    """Pulse count for a digit, where **0 is sent as ten pulses**."""
    if not 0 <= digit <= 9:
        raise ValueError(f"digit out of range: {digit}")
    return 10 if digit == 0 else digit


def pulse_train(
    digit: int,
    t0: float = 0.0,
    pps: float = DEFAULT_PPS,
    break_ratio: float = DEFAULT_BREAK_RATIO,
    bounce_ms: float = 0.0,
    bounce_count: int = 0,
    jitter_ms: float = 0.0,
    rng: Optional[random.Random] = None,
) -> List[Edge]:
    """Generate the contact edges for a single dialed ``digit``.

    Args:
        t0: Start time in milliseconds.
        pps: Pulses per second (10 is nominal; real dials drift 8-11).
        break_ratio: Fraction of each cycle the contact is **open**.
        bounce_ms: Spread of spurious bounce transitions after each real edge.
        bounce_count: Number of bounce transition pairs to inject per edge.
        jitter_ms: Uniform +/- timing jitter applied to each real edge.
        rng: Optional seeded RNG, for reproducible tests.

    Returns:
        Chronologically ordered ``(t_ms, closed)`` edges.
    """
    rng = rng or random.Random(0)
    period = 1000.0 / pps
    break_ms = period * break_ratio

    edges: List[Edge] = []

    def emit(t: float, closed: bool) -> None:
        jittered = t + (rng.uniform(-jitter_ms, jitter_ms) if jitter_ms else 0.0)
        edges.append((jittered, closed))
        # Contact bounce: rapid chatter immediately after the real transition.
        for i in range(bounce_count):
            offset = bounce_ms * (i + 1) / (bounce_count + 1)
            edges.append((jittered + offset, not closed))
            edges.append((jittered + offset + bounce_ms / (bounce_count + 2), closed))

    for i in range(digit_to_pulses(digit)):
        cycle = t0 + i * period
        emit(cycle, False)              # contact opens — one pulse
        emit(cycle + break_ms, True)    # contact closes again

    edges.sort(key=lambda e: e[0])
    return edges


def number_train(
    number: Sequence[int] | str,
    t0: float = 0.0,
    interdigit_ms: float = DEFAULT_INTERDIGIT_MS,
    **kwargs,
) -> List[Edge]:
    """Generate edges for a whole dialed number.

    ``interdigit_ms`` models the time the dial takes to return plus the user
    moving a finger to the next hole.
    """
    digits = [int(c) for c in number] if isinstance(number, str) else list(number)

    edges: List[Edge] = []
    t = t0
    for digit in digits:
        train = pulse_train(digit, t0=t, **kwargs)
        edges.extend(train)
        t = train[-1][0] + interdigit_ms
    return edges


def replay(decoder, edges: Sequence[Edge], tick_every_ms: float = 10.0) -> None:
    """Feed ``edges`` into a decoder, interleaving realistic periodic ticks.

    This mirrors how a real event loop would poll: edges arrive as interrupts,
    and ``tick()`` runs on a timer to close out a digit after the inter-digit
    gap. Without the interleaved ticks a test would not prove the timeout path.
    """
    if not edges:
        return
    t = edges[0][0]
    for t_ms, closed in edges:
        while t < t_ms:
            decoder.tick(t)
            t += tick_every_ms
        decoder.edge(t_ms, closed)

    # Drain past the end so the final digit's inter-digit timeout elapses.
    end = edges[-1][0] + max(decoder.interdigit_ms * 2, 500.0)
    while t < end:
        decoder.tick(t)
        t += tick_every_ms
