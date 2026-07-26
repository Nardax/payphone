"""Rotary dial pulse decoder.

A rotary dial's pulse contact sits **closed** at rest. Dialing digit *N* opens
the loop *N* times at roughly 10 pulses per second. Digit ``0`` is sent as
**ten** pulses, not zero.

North American dials use an approximate **39% make / 61% break** ratio, so at
10pps each pulse cycle is ~100ms: ~61ms open, then ~39ms closed.

This module is intentionally pure logic — no GPIO, no timers, no I/O. Callers
feed it edge events and periodic ticks, which makes it fully testable against
synthetic pulse trains (see :mod:`payphone.pulse_synth`) and equally usable
from a real GPIO interrupt handler.

Typical use::

    dec = RotaryDialDecoder(on_digit=print)
    dec.edge(t_ms, closed=False)   # contact opened  (pulse begins)
    dec.edge(t_ms, closed=True)    # contact closed  (pulse ends)
    dec.tick(now_ms)               # call periodically to flush a finished digit
"""

from __future__ import annotations

from typing import Callable, List, Optional

# Defaults tuned for a standard 10pps North American dial.
DEFAULT_DEBOUNCE_MS = 8.0
DEFAULT_INTERDIGIT_MS = 250.0
MAX_PULSES_PER_DIGIT = 10


def pulses_to_digit(pulses: int) -> int:
    """Convert a pulse count (1-10) to its digit, where **10 pulses = 0**."""
    if not 1 <= pulses <= MAX_PULSES_PER_DIGIT:
        raise ValueError(f"pulse count out of range: {pulses}")
    return 0 if pulses == MAX_PULSES_PER_DIGIT else pulses


class RotaryDialDecoder:
    """Decodes rotary dial pulse edges into digits.

    Args:
        debounce_ms: Edges arriving within this window of the previously
            accepted edge are treated as contact bounce and ignored.
        interdigit_ms: How long the contact must rest closed before the
            accumulated pulses are emitted as a completed digit.
        on_digit: Called with each decoded digit (0-9).
        on_error: Called with a message when a pulse burst is unusable (for
            example a partial-rotation misdial producing more than 10 pulses).
    """

    def __init__(
        self,
        debounce_ms: float = DEFAULT_DEBOUNCE_MS,
        interdigit_ms: float = DEFAULT_INTERDIGIT_MS,
        on_digit: Optional[Callable[[int], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.debounce_ms = debounce_ms
        self.interdigit_ms = interdigit_ms
        self.on_digit = on_digit
        self.on_error = on_error

        self.digits: List[int] = []
        self._pulses = 0
        self._closed = True           # contact rests closed
        self._last_edge_ms: Optional[float] = None
        self._last_close_ms: Optional[float] = None

    # -- input -----------------------------------------------------------

    def edge(self, t_ms: float, closed: bool) -> None:
        """Feed a contact transition. ``closed=False`` means the loop opened."""
        if closed == self._closed:
            return  # no actual change of state

        if (
            self._last_edge_ms is not None
            and t_ms - self._last_edge_ms < self.debounce_ms
        ):
            return  # contact bounce — ignore

        self._closed = closed
        self._last_edge_ms = t_ms

        if not closed:
            # Loop just opened: that is one pulse.
            self._pulses += 1
            self._last_close_ms = None
        else:
            # Loop closed again: start measuring the inter-digit gap.
            self._last_close_ms = t_ms

    def tick(self, now_ms: float) -> None:
        """Emit a digit once the contact has rested closed long enough."""
        if self._pulses == 0 or not self._closed or self._last_close_ms is None:
            return
        if now_ms - self._last_close_ms < self.interdigit_ms:
            return
        self._flush()

    def flush(self) -> None:
        """Force-emit any buffered digit (e.g. when the handset goes on-hook)."""
        if self._pulses:
            self._flush()

    # -- internals -------------------------------------------------------

    def _flush(self) -> None:
        pulses, self._pulses = self._pulses, 0
        self._last_close_ms = None
        try:
            digit = pulses_to_digit(pulses)
        except ValueError:
            if self.on_error:
                self.on_error(f"discarding unusable pulse burst: {pulses} pulses")
            return
        self.digits.append(digit)
        if self.on_digit:
            self.on_digit(digit)

    # -- convenience -----------------------------------------------------

    @property
    def number(self) -> str:
        """Digits decoded so far, as a string."""
        return "".join(str(d) for d in self.digits)

    def reset(self) -> None:
        """Clear all decoded digits and pulse state."""
        self.digits.clear()
        self._pulses = 0
        self._closed = True
        self._last_edge_ms = None
        self._last_close_ms = None
