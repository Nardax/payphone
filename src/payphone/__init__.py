"""Payphone control software (Version 2 — Raspberry Pi brain).

Pure-logic modules here are deliberately free of any GPIO or browser imports so
they can be unit-tested on any machine, with no Raspberry Pi and no payphone
hardware attached.
"""

__all__ = ["dial_decoder", "pulse_synth"]
