#!/usr/bin/env python3
"""Google Voice call control for the payphone — dial / answer / hang up / watch.

This is the project's **highest-risk unknown** (task ``sw-call-control``): a
human can place a Google Voice call in Chromium, but can a *script*? Everything
downstream — the rotary dial, the hook switch, the bell — is pointless if this
cannot be automated.

Approach: attach to an **already-running** Chromium over the Chrome DevTools
Protocol. This matters on a Raspberry Pi because Playwright ships **no prebuilt
ARM Chromium**, so ``playwright install`` will not give you a usable browser.
Attaching to the system Chromium sidesteps that completely *and* reuses your
existing Google login.

Setup (once, on the Pi)::

    sudo apt install -y chromium python3-pip
    pip3 install --break-system-packages playwright
    # NOTE: do NOT run `playwright install` — no ARM build exists; we attach instead.

Start Chromium with the debug port, logged into Google Voice::

    chromium --remote-debugging-port=9222 \
             --user-data-dir=$HOME/.config/payphone-chromium \
             https://voice.google.com/u/0/calls

Then::

    python3 tools/gvcall.py probe                 # FIRST: dump the real DOM
    python3 tools/gvcall.py status
    python3 tools/gvcall.py dial 5551234567
    python3 tools/gvcall.py answer
    python3 tools/gvcall.py hangup
    python3 tools/gvcall.py watch                 # emit events on inbound ring

``probe`` exists because the selectors in ``payphone/gv_selectors.py`` are
unverified guesses. Run it first and fix that file — it is designed to be the
only thing you need to edit when Google reshuffles their DOM.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from payphone import gv_selectors as sel  # noqa: E402

DEFAULT_CDP = "http://localhost:9222"
POLL_INTERVAL_S = 0.5


# --------------------------------------------------------------------------
# browser plumbing
# --------------------------------------------------------------------------

def connect(cdp_url: str):
    """Attach to a running Chromium over CDP. Returns (playwright, browser)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit(
            "ERROR: playwright not installed.\n"
            "    pip3 install --break-system-packages playwright\n"
            "(Do NOT run `playwright install` on a Pi — no ARM browser build exists.)"
        )

    pw = sync_playwright().start()
    try:
        browser = pw.chromium.connect_over_cdp(cdp_url)
    except Exception as exc:  # noqa: BLE001
        pw.stop()
        sys.exit(
            f"ERROR: could not attach to Chromium at {cdp_url}\n  {exc}\n\n"
            "Start Chromium with the debug port first:\n"
            "    chromium --remote-debugging-port=9222 \\\n"
            "             --user-data-dir=$HOME/.config/payphone-chromium \\\n"
            "             https://voice.google.com/u/0/calls"
        )
    return pw, browser


def find_gv_page(browser):
    """Locate the tab showing Google Voice."""
    for context in browser.contexts:
        for page in context.pages:
            if sel.GV_URL_PREFIX in (page.url or ""):
                return page
    # Fall back to opening it in the existing context.
    if browser.contexts:
        page = browser.contexts[0].new_page()
        page.goto(sel.GV_CALLS_URL)
        page.wait_for_load_state("domcontentloaded")
        return page
    sys.exit("ERROR: no browser context found. Is Chromium actually running?")


def first_visible(page, candidates: List[str], timeout_ms: int = 2000):
    """Return the first candidate selector that matches a visible element."""
    deadline = time.time() + timeout_ms / 1000.0
    while time.time() < deadline:
        for selector in candidates:
            try:
                loc = page.locator(selector).first
                if loc.is_visible(timeout=250):
                    return loc
            except Exception:  # noqa: BLE001 — selector may be invalid/absent
                continue
        time.sleep(0.15)
    return None


def any_visible(page, candidates: List[str]) -> bool:
    return first_visible(page, candidates, timeout_ms=600) is not None


# --------------------------------------------------------------------------
# commands
# --------------------------------------------------------------------------

def cmd_probe(page, _args) -> int:
    """Dump every visible interactive element, to repair selectors."""
    js = """
    () => Array.from(document.querySelectorAll('button,[role="button"],input'))
      .filter(el => el.offsetParent !== null)
      .slice(0, 120)
      .map(el => ({
        tag: el.tagName.toLowerCase(),
        aria: el.getAttribute('aria-label'),
        text: (el.innerText || el.value || '').trim().slice(0, 60),
        type: el.getAttribute('type'),
        placeholder: el.getAttribute('placeholder'),
      }));
    """
    print(f"URL: {page.url}\n")
    elements = page.evaluate(js)
    if not elements:
        print("No visible interactive elements found. Is the page still loading, "
              "or are you signed out?")
        return 1
    print(f"{len(elements)} visible interactive element(s):\n")
    for el in elements:
        print(json.dumps(el, ensure_ascii=False))
    print("\nPaste the relevant aria-labels into src/payphone/gv_selectors.py")
    return 0


def cmd_status(page, _args) -> int:
    incoming = any_visible(page, sel.INCOMING_CALL_INDICATOR)
    in_call = any_visible(page, sel.IN_CALL_INDICATOR)
    state = "ringing" if incoming else ("in-call" if in_call else "idle")
    print(json.dumps({"state": state, "url": page.url}))
    return 0


def cmd_dial(page, args) -> int:
    number = "".join(ch for ch in args.number if ch.isdigit() or ch == "+")
    if not number:
        print("ERROR: no digits in number", file=sys.stderr)
        return 2

    if sel.GV_URL_PREFIX not in (page.url or ""):
        page.goto(sel.GV_CALLS_URL)
        page.wait_for_load_state("domcontentloaded")

    box = first_visible(page, sel.NUMBER_INPUT, timeout_ms=8000)
    if box is None:
        print("ERROR: could not find the number input.\n"
              "Run `gvcall.py probe` and update NUMBER_INPUT in gv_selectors.py.",
              file=sys.stderr)
        return 1

    box.click()
    box.fill("")
    box.type(number, delay=60)
    time.sleep(0.6)

    button = first_visible(page, sel.CALL_BUTTON, timeout_ms=4000)
    if button is None:
        # Some builds accept Enter in the search box.
        box.press("Enter")
        time.sleep(1.0)
        button = first_visible(page, sel.CALL_BUTTON, timeout_ms=4000)
    if button is None:
        print("ERROR: could not find the Call button.\n"
              "Run `gvcall.py probe` and update CALL_BUTTON in gv_selectors.py.",
              file=sys.stderr)
        return 1

    button.click()
    print(f"dialing {number}")
    return 0


def cmd_answer(page, _args) -> int:
    button = first_visible(page, sel.ANSWER_BUTTON, timeout_ms=4000)
    if button is None:
        print("ERROR: no Answer button visible (is a call actually ringing?)",
              file=sys.stderr)
        return 1
    button.click()
    print("answered")
    return 0


def cmd_hangup(page, _args) -> int:
    button = first_visible(page, sel.HANGUP_BUTTON, timeout_ms=4000)
    if button is None:
        print("ERROR: no Hang up button visible (is a call actually active?)",
              file=sys.stderr)
        return 1
    button.click()
    print("hung up")
    return 0


def cmd_watch(page, args) -> int:
    """Poll for inbound calls and emit one JSON event per state change.

    This is the signal that will eventually fire the bell (task
    ``sw-ring-cadence``). Pipe it into another process, or import the same
    polling logic from a service.
    """
    print(f"watching {page.url} — Ctrl-C to stop", file=sys.stderr)
    last = None
    try:
        while True:
            if any_visible(page, sel.INCOMING_CALL_INDICATOR):
                state = "ringing"
            elif any_visible(page, sel.IN_CALL_INDICATOR):
                state = "in-call"
            else:
                state = "idle"

            if state != last:
                print(json.dumps({"event": "state", "state": state,
                                  "ts": round(time.time(), 3)}), flush=True)
                last = state
            time.sleep(args.interval)
    except KeyboardInterrupt:
        return 0


COMMANDS = {
    "probe": cmd_probe,
    "status": cmd_status,
    "dial": cmd_dial,
    "answer": cmd_answer,
    "hangup": cmd_hangup,
    "watch": cmd_watch,
}


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cdp", default=DEFAULT_CDP,
                    help=f"Chromium CDP endpoint (default: {DEFAULT_CDP})")
    sub = ap.add_subparsers(dest="command", required=True)

    sub.add_parser("probe", help="dump visible elements to repair selectors")
    sub.add_parser("status", help="report idle / ringing / in-call")
    p_dial = sub.add_parser("dial", help="place an outbound call")
    p_dial.add_argument("number")
    sub.add_parser("answer", help="answer a ringing call")
    sub.add_parser("hangup", help="end the active call")
    p_watch = sub.add_parser("watch", help="stream call-state events as JSON")
    p_watch.add_argument("--interval", type=float, default=POLL_INTERVAL_S)

    args = ap.parse_args()

    pw, browser = connect(args.cdp)
    try:
        page = find_gv_page(browser)
        return COMMANDS[args.command](page, args)
    finally:
        try:
            browser.close()
        except Exception:  # noqa: BLE001
            pass
        pw.stop()


if __name__ == "__main__":
    raise SystemExit(main())
