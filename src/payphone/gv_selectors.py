"""Google Voice web-app selectors — the one file you edit when Google changes the DOM.

⚠️ **These are unverified starting points, not gospel.** The Google Voice web app
is a private, unstable interface with obfuscated class names. Selectors WILL rot.

Each entry is an ordered list of candidate selectors; the first one that matches
a visible element wins. Prefer, in order:

1. ``aria-label`` / ``role`` — Google maintains these for accessibility, so they
   survive far longer than class names.
2. Visible text.
3. Structural CSS — last resort, breaks on any redesign.

**Before trusting any of this, run:** ``python3 tools/gvcall.py probe``
That dumps every visible button with its aria-label and text, so you can paste
the real values in here.
"""

from __future__ import annotations

GV_CALLS_URL = "https://voice.google.com/u/0/calls"
GV_URL_PREFIX = "https://voice.google.com"

# Text/number entry for placing a call.
NUMBER_INPUT = [
    'input[aria-label*="Search contacts and places" i]',
    'input[aria-label*="Enter a name or number" i]',
    'input[placeholder*="name or number" i]',
    'input[type="tel"]',
    'gv-search-box input',
]

# Button that starts the outbound call.
CALL_BUTTON = [
    'button[aria-label*="Call" i]:not([aria-label*="Hang" i])',
    'button[aria-label*="Place call" i]',
    '[role="button"][aria-label*="Call" i]',
    'button:has-text("Call")',
]

# Button that answers an inbound call.
ANSWER_BUTTON = [
    'button[aria-label*="Answer" i]',
    'button[aria-label*="Accept" i]',
    '[role="button"][aria-label*="Answer" i]',
    'button:has-text("Answer")',
]

# Button that ends the current call.
HANGUP_BUTTON = [
    'button[aria-label*="Hang up" i]',
    'button[aria-label*="End call" i]',
    'button[aria-label*="Decline" i]',
    '[role="button"][aria-label*="Hang up" i]',
    'button:has-text("Hang up")',
]

# Presence of any of these implies a call is currently ringing IN.
INCOMING_CALL_INDICATOR = [
    'button[aria-label*="Answer" i]',
    '[aria-label*="Incoming call" i]',
    'text=/incoming call/i',
]

# Presence of any of these implies a call is currently connected.
IN_CALL_INDICATOR = [
    'button[aria-label*="Hang up" i]',
    'button[aria-label*="End call" i]',
    '[aria-label*="Mute" i]',
]
