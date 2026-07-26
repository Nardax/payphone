"""Unit tests for the rotary dial pulse decoder.

Runs anywhere with stdlib only — no Raspberry Pi, no payphone, no pip installs::

    python -m unittest discover -s tests -v
"""

import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from payphone.dial_decoder import RotaryDialDecoder, pulses_to_digit  # noqa: E402
from payphone import pulse_synth  # noqa: E402


def decode(number, **kwargs):
    """Synthesize a dialed number, decode it, and return the decoded string."""
    synth_kwargs = {
        k: kwargs.pop(k)
        for k in ("pps", "break_ratio", "bounce_ms", "bounce_count", "jitter_ms", "rng")
        if k in kwargs
    }
    interdigit = kwargs.pop("interdigit_ms", pulse_synth.DEFAULT_INTERDIGIT_MS)
    dec = RotaryDialDecoder(**kwargs)
    edges = pulse_synth.number_train(number, interdigit_ms=interdigit, **synth_kwargs)
    pulse_synth.replay(dec, edges)
    return dec.number


class TestPulsesToDigit(unittest.TestCase):
    def test_one_through_nine_map_directly(self):
        for pulses in range(1, 10):
            self.assertEqual(pulses_to_digit(pulses), pulses)

    def test_ten_pulses_is_zero(self):
        """The classic rotary gotcha: '0' is ten pulses, not zero."""
        self.assertEqual(pulses_to_digit(10), 0)

    def test_out_of_range_rejected(self):
        for bad in (0, -1, 11, 99):
            with self.assertRaises(ValueError):
                pulses_to_digit(bad)


class TestCleanSignal(unittest.TestCase):
    def test_every_single_digit(self):
        for digit in range(10):
            self.assertEqual(decode(str(digit)), str(digit), f"digit {digit}")

    def test_zero_is_not_silently_dropped(self):
        self.assertEqual(decode("0"), "0")

    def test_seven_digit_number(self):
        self.assertEqual(decode("5551234"), "5551234")

    def test_ten_digit_number_with_zeros(self):
        self.assertEqual(decode("5030867900"), "5030867900")

    def test_repeated_digits_are_not_merged(self):
        self.assertEqual(decode("111"), "111")
        self.assertEqual(decode("000"), "000")


class TestContactBounce(unittest.TestCase):
    """Real dial contacts chatter; the decoder must debounce them."""

    def test_bounce_does_not_inflate_pulse_count(self):
        self.assertEqual(
            decode("5551234", bounce_ms=2.0, bounce_count=2),
            "5551234",
        )

    def test_heavy_bounce_on_worst_case_digit_zero(self):
        # Ten pulses means ten chances for bounce to add a phantom digit.
        self.assertEqual(decode("0", bounce_ms=3.0, bounce_count=3), "0")

    def test_undebounced_decoder_would_miscount(self):
        """Guards the test itself: without debounce, bounce must break it.

        If this ever passes, the synthetic bounce is too gentle to be a
        meaningful test of the debounce logic.
        """
        dec = RotaryDialDecoder(debounce_ms=0.0)
        edges = pulse_synth.number_train("5", bounce_ms=3.0, bounce_count=3)
        pulse_synth.replay(dec, edges)
        self.assertNotEqual(dec.number, "5")


class TestTimingTolerance(unittest.TestCase):
    """Worn mechanical dials drift; decoding must not be brittle."""

    def test_slow_dial_8pps(self):
        self.assertEqual(decode("5551234", pps=8.0), "5551234")

    def test_fast_dial_11pps(self):
        self.assertEqual(decode("5551234", pps=11.0), "5551234")

    def test_jittered_edges(self):
        rng = random.Random(1234)
        self.assertEqual(decode("9080706", jitter_ms=4.0, rng=rng), "9080706")

    def test_off_ratio_dial(self):
        # Some dials sit closer to 50/50 than the nominal 39/61.
        self.assertEqual(decode("5551234", break_ratio=0.5), "5551234")

    def test_short_interdigit_gap_still_separates_digits(self):
        self.assertEqual(decode("123", interdigit_ms=300.0), "123")


class TestDigitSeparation(unittest.TestCase):
    def test_gap_shorter_than_timeout_merges_digits(self):
        """Documents the failure mode if inter-digit timing is set too loose.

        A 120ms gap is shorter than the 250ms timeout, so 1 then 2 is read as a
        single 3-pulse burst -> '3'. This is why interdigit_ms must sit between
        the intra-digit gap (~39ms) and a real user's inter-digit pause.
        """
        self.assertEqual(decode("12", interdigit_ms=120.0), "3")

    def test_intra_digit_gaps_never_split_a_digit(self):
        # 39ms make intervals inside digit 9 must not be read as digit breaks.
        self.assertEqual(decode("9"), "9")


class TestCallbacksAndState(unittest.TestCase):
    def test_on_digit_fires_in_order(self):
        seen = []
        dec = RotaryDialDecoder(on_digit=seen.append)
        pulse_synth.replay(dec, pulse_synth.number_train("406"))
        self.assertEqual(seen, [4, 0, 6])

    def test_flush_emits_pending_digit(self):
        """Hanging up mid-digit should still surface what was dialed."""
        dec = RotaryDialDecoder()
        for t_ms, closed in pulse_synth.pulse_train(7):
            dec.edge(t_ms, closed)
        self.assertEqual(dec.number, "")  # timeout has not elapsed yet
        dec.flush()
        self.assertEqual(dec.number, "7")

    def test_reset_clears_state(self):
        dec = RotaryDialDecoder()
        pulse_synth.replay(dec, pulse_synth.number_train("55"))
        self.assertEqual(dec.number, "55")
        dec.reset()
        self.assertEqual(dec.number, "")
        pulse_synth.replay(dec, pulse_synth.number_train("1"))
        self.assertEqual(dec.number, "1")

    def test_overlong_burst_is_reported_not_crashed(self):
        errors = []
        dec = RotaryDialDecoder(on_error=errors.append)
        # 13 pulses: a jammed or over-rotated dial.
        for i in range(13):
            dec.edge(i * 100.0, False)
            dec.edge(i * 100.0 + 61.0, True)
        dec.tick(13 * 100.0 + 500.0)
        self.assertEqual(dec.number, "")
        self.assertEqual(len(errors), 1)

    def test_duplicate_edges_are_ignored(self):
        dec = RotaryDialDecoder()
        dec.edge(0.0, False)
        dec.edge(1.0, False)   # same state repeated — must not count twice
        dec.edge(61.0, True)
        dec.tick(500.0)
        self.assertEqual(dec.number, "1")


if __name__ == "__main__":
    unittest.main(verbosity=2)
