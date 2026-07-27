"""Google Voice web-app selectors — the one file you edit when Google changes the DOM.

Status legend:
    VERIFIED    — observed in a real `gvcall.py probe` dump against a live
                  signed-in Google Voice session.
    UNVERIFIED  — still a guess; needs a probe taken *during a live call*.

The Google Voice web app is a private, obfuscated interface, so selectors will
rot. Prefer ``aria-label``/``role`` (Google maintains these for accessibility)
over text, and text over structural CSS.

Regenerate the evidence with::

    python3 tools/gvcall.py probe
"""

from __future__ import annotations

GV_CALLS_URL = "https://voice.google.com/u/0/calls"
GV_URL_PREFIX = "https://voice.google.com"

# VERIFIED. The dial field has NO aria-label — it is identified by placeholder.
# Must not match the top-of-page search box, which is
# input[aria-label="Search"] with placeholder "Search Google Voice".
NUMBER_INPUT = [
    'input[placeholder="Enter a name or number"]',
    'input[placeholder*="name or number" i]',
    'input[type="tel"]',
]

# VERIFIED (idle state). The call button is icon-only: its text is the Material
# ligature "call", and its aria-label is "No contact selected" until a number is
# entered, at which point it becomes "Call <number>".
#
# TRAP: do NOT use `button:has-text("Call")`. A *different* button — the
# "Call Availability settings" control — contains that text and appears EARLIER
# in the DOM, so `.first` would silently open settings instead of dialing.
# That button has aria-label=null, which is why the aria-label selectors below
# are safe, and why the text fallback uses exact-match `:text-is("call")`
# rather than a substring match.
CALL_BUTTON = [
    'button[aria-label^="Call" i]',
    'button:text-is("call")',
    'button[aria-label="No contact selected"]',
]

# VERIFIED. The on-screen keypad. aria-labels are quoted digits, and keys 2-9
# append their letters (e.g. "'2' 'a' 'b' 'c'"), so match on the prefix.
# Clicking these digit-by-digit mirrors how the rotary dial will actually feed
# digits as they are decoded.
KEYPAD_STAR = 'button[aria-label="Star"]'
KEYPAD_POUND = 'button[aria-label="Pound"]'


def keypad_digit(digit: int | str) -> str:
    """CSS selector for an on-screen keypad key.

    Accepts 0-9 as int or str, plus "*" and "#".
    """
    if digit == "*":
        return KEYPAD_STAR
    if digit == "#":
        return KEYPAD_POUND
    value = int(digit)
    if not 0 <= value <= 9:
        raise ValueError(f"digit out of range: {digit}")
    return f"button[aria-label^=\"'{value}'\"]"


# UNVERIFIED — no call was active during the probe, so these did not appear.
# Re-run `gvcall.py probe` while a call is RINGING and again while CONNECTED,
# then replace these with the observed aria-labels.
ANSWER_BUTTON = [
    'button[aria-label*="Answer" i]',
    'button[aria-label*="Accept" i]',
    '[role="button"][aria-label*="Answer" i]',
]

# UNVERIFIED — see note above.
HANGUP_BUTTON = [
    'button[aria-label*="Hang up" i]',
    'button[aria-label*="End call" i]',
    'button[aria-label*="Decline" i]',
    '[role="button"][aria-label*="Hang up" i]',
]

# UNVERIFIED. Presence implies a call is ringing IN — this is what will
# eventually fire the bell.
INCOMING_CALL_INDICATOR = [
    'button[aria-label*="Answer" i]',
    '[aria-label*="Incoming call" i]',
]

# UNVERIFIED. Presence implies a call is connected.
IN_CALL_INDICATOR = [
    'button[aria-label*="Hang up" i]',
    'button[aria-label*="End call" i]',
    'button[aria-label*="Mute" i]',
]

# VERIFIED. Useful later for routing call audio to the USB sound card.
AUDIO_SETTINGS_BUTTON = 'button[aria-label="Audio settings"]'
