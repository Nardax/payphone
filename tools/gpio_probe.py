#!/usr/bin/env python3
"""Turn the Pi into a logic analyzer for tracing payphone contacts.

A multimeter is great for finding *which* wires are which, but it is poor at
catching a rotary dial's 10-pulses-per-second chatter — the needle or beeper
simply can't keep up. This tool watches a GPIO pin and reports exactly what the
contact is doing, including live digit decoding using the very same decoder that
will run in the finished phone.

Use it to complete `reverse-wiring` and to prove `v2-dial-hook` before
committing to permanent wiring.

⚠️ **SAFETY — dry contacts only.**
Only ever connect a contact pair you have *already verified with the multimeter*
to be **fully isolated**: no path to the line (tip/ring), no path to the network
coil, and **no path to the ringer or its series capacitor**. A capacitor can hold
charge, and the ⚠️ **~90V AC ring circuit will destroy the Pi instantly.** Never
connect the ring generator to a GPIO — that path is opto-isolated, always.

Wiring for a dry contact (no external power needed)::

    contact leg A ---- 1k resistor ---- GPIO pin   (internal pull-up enabled)
    contact leg B ---- GND

The 1k series resistor is cheap insurance against a mis-identified wire.

Usage on the Pi::

    python3 tools/gpio_probe.py hook --pin 22      # watch the hookswitch
    python3 tools/gpio_probe.py dial --pin 17      # live-decode dialed digits
    python3 tools/gpio_probe.py edges --pin 17     # raw transitions + timing
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from payphone.dial_decoder import RotaryDialDecoder  # noqa: E402

SAMPLE_INTERVAL_S = 0.0005  # 0.5ms


def open_pin(pin: int, pull_up: bool = True):
    try:
        from gpiozero import DigitalInputDevice
    except ImportError:
        sys.exit("ERROR: gpiozero not available. On Raspberry Pi OS:\n"
                 "    sudo apt install -y python3-gpiozero\n"
                 "This script must run on the Pi itself.")
    return DigitalInputDevice(pin, pull_up=pull_up)


def banner(pin: int, closed_is: str) -> None:
    print(f"Watching GPIO{pin} (internal pull-up).")
    print(f"With a dry contact to GND: {closed_is}")
    print("Ctrl-C to stop.\n")


def cmd_edges(args) -> int:
    """Print every transition with the time since the previous one."""
    dev = open_pin(args.pin)
    banner(args.pin, "LOW = contact CLOSED, HIGH = contact OPEN")
    last = dev.value
    t0 = time.perf_counter()
    last_t = t0
    count = 0
    try:
        while True:
            v = dev.value
            if v != last:
                now = time.perf_counter()
                delta_ms = (now - last_t) * 1000.0
                state = "OPEN " if v else "CLOSED"
                count += 1
                print(f"[{(now - t0) * 1000:9.1f} ms] {state}  "
                      f"(held {delta_ms:7.1f} ms)")
                last, last_t = v, now
            time.sleep(SAMPLE_INTERVAL_S)
    except KeyboardInterrupt:
        print(f"\n{count} transitions observed.")
        return 0
    finally:
        dev.close()


def cmd_hook(args) -> int:
    """Report on-hook / off-hook changes — hang up and lift to identify."""
    dev = open_pin(args.pin)
    banner(args.pin, "LOW = contact CLOSED, HIGH = contact OPEN")
    print("Lift and replace the handset a few times.\n")
    last = None
    try:
        while True:
            closed = not dev.value  # pull-up: LOW means shorted to GND
            if closed != last:
                print(f"  contact {'CLOSED' if closed else 'OPEN  '}"
                      f"   <- {'handset DOWN?' if closed else 'handset UP?'}")
                last = closed
            time.sleep(0.02)
    except KeyboardInterrupt:
        print("\nNote which physical position gave which reading, then record it "
              "in docs/WIRING-WORKSHEET.md.")
        return 0
    finally:
        dev.close()


def cmd_dial(args) -> int:
    """Live-decode rotary digits using the production decoder."""
    dev = open_pin(args.pin)
    decoder = RotaryDialDecoder(
        on_digit=lambda d: print(f"  digit: {d}    (so far: {decoder.number})"),
        on_error=lambda m: print(f"  !! {m}"),
    )
    banner(args.pin, "LOW = contact CLOSED (loop intact), HIGH = pulse (open)")
    print("Dial some digits. Try '0' — it should decode as 0, not 10.\n")

    t0 = time.perf_counter()
    last = None
    try:
        while True:
            t_ms = (time.perf_counter() - t0) * 1000.0
            closed = not dev.value
            if closed != last:
                decoder.edge(t_ms, closed)
                last = closed
            decoder.tick(t_ms)
            time.sleep(SAMPLE_INTERVAL_S)
    except KeyboardInterrupt:
        decoder.flush()
        print(f"\nDecoded: {decoder.number or '(nothing)'}")
        if not decoder.number:
            print("Nothing decoded. Likely causes:\n"
                  "  - wrong contact pair (this may be the off-normal pair, which\n"
                  "    stays closed for the whole rotation instead of pulsing)\n"
                  "  - contact not actually reaching GND\n"
                  "  - try `gpio_probe.py edges` to see raw transitions")
        return 0
    finally:
        dev.close()


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("edges", "print raw transitions with timing"),
        ("hook", "identify the hookswitch contact"),
        ("dial", "live-decode rotary digits"),
    ):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("--pin", type=int, required=True, help="BCM pin number")

    args = ap.parse_args()
    return {"edges": cmd_edges, "hook": cmd_hook, "dial": cmd_dial}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
