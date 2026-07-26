#!/usr/bin/env python3
"""GPIO loopback bench test for the rotary dial decoder.

Proves the decoder works against **real GPIO timing** with no payphone attached.
Total cost: one jumper wire.

    Pi GPIO 17 (out)  ---- jumper ----  Pi GPIO 27 (in)

The script replays a synthetic rotary pulse train onto the output pin, samples
the input pin in real time, decodes it, and compares against what was "dialed".
Because it reuses :mod:`payphone.pulse_synth`, the waveform here is identical to
the one the unit tests use — so a pass means the logic survives real scheduling
jitter, not just idealised timestamps.

Run on the Pi::

    python3 tools/gpio_loopback.py                  # dial 5551234567
    python3 tools/gpio_loopback.py --number 0       # worst case: ten pulses
    python3 tools/gpio_loopback.py --bounce         # simulate dirty contacts
    python3 tools/gpio_loopback.py --out 17 --in 27

Convention: output HIGH == contact closed (loop intact), LOW == pulse (open).
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from payphone import pulse_synth  # noqa: E402
from payphone.dial_decoder import RotaryDialDecoder  # noqa: E402

SAMPLE_INTERVAL_S = 0.0005  # 0.5ms — plenty for 39/61ms pulse features


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--number", default="5551234567",
                    help="digits to 'dial' onto the wire (default: 5551234567)")
    ap.add_argument("--out", dest="out_pin", type=int, default=17,
                    help="BCM pin driven as the dial contact (default: 17)")
    ap.add_argument("--in", dest="in_pin", type=int, default=27,
                    help="BCM pin that reads it back (default: 27)")
    ap.add_argument("--pps", type=float, default=10.0,
                    help="pulses per second (default: 10)")
    ap.add_argument("--bounce", action="store_true",
                    help="inject contact bounce to stress the debounce logic")
    ap.add_argument("--interdigit-ms", type=float, default=600.0,
                    help="gap between digits in ms (default: 600)")
    return ap.parse_args()


def main() -> int:
    args = parse_args()

    try:
        from gpiozero import DigitalInputDevice, DigitalOutputDevice
    except ImportError:
        print("ERROR: gpiozero not available. On Raspberry Pi OS:\n"
              "    sudo apt install -y python3-gpiozero\n"
              "This script must run on the Pi itself.", file=sys.stderr)
        return 2

    synth_kwargs = {"pps": args.pps}
    if args.bounce:
        synth_kwargs.update(bounce_ms=3.0, bounce_count=3)

    edges = pulse_synth.number_train(
        args.number, interdigit_ms=args.interdigit_ms, **synth_kwargs
    )

    print(f"Loopback: GPIO{args.out_pin} (out) --> GPIO{args.in_pin} (in)")
    print(f"Dialing {args.number!r}  ({len(edges)} edges, "
          f"{args.pps}pps, bounce={'on' if args.bounce else 'off'})")
    print("Make sure the jumper is connected.\n")

    out = DigitalOutputDevice(args.out_pin, initial_value=True)   # rest = closed
    pin_in = DigitalInputDevice(args.in_pin)

    decoder = RotaryDialDecoder(on_digit=lambda d: print(f"  decoded digit: {d}"))

    last_sampled = pin_in.value
    t_start = time.perf_counter()

    def now_ms() -> float:
        return (time.perf_counter() - t_start) * 1000.0

    edge_iter = iter(edges)
    next_edge = next(edge_iter, None)
    end_ms = edges[-1][0] + max(decoder.interdigit_ms * 2, 800.0)

    while True:
        t = now_ms()

        # Drive scheduled transitions onto the output pin.
        while next_edge is not None and t >= next_edge[0]:
            out.value = bool(next_edge[1])   # closed -> HIGH
            next_edge = next(edge_iter, None)

        # Sample the input pin and feed real observed transitions to the decoder.
        sampled = pin_in.value
        if sampled != last_sampled:
            decoder.edge(t, bool(sampled))
            last_sampled = sampled
        decoder.tick(t)

        if next_edge is None and t >= end_ms:
            break
        time.sleep(SAMPLE_INTERVAL_S)

    decoder.flush()
    out.close()
    pin_in.close()

    expected = args.number
    actual = decoder.number
    print(f"\n  expected: {expected}\n  decoded : {actual}")

    if actual == expected:
        print("\nPASS — decoder survived real GPIO timing.")
        return 0

    print("\nFAIL — decoded output does not match.")
    print("Check: is the jumper actually connecting the two pins?")
    print("If the jumper is good, this is a real timing/debounce bug worth fixing "
          "now, while it is still cheap to fix.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
