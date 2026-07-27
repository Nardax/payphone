# Software — Raspberry Pi control stack

Control software for the Version 2 (Raspberry Pi) build. Companion to
[PLAN.md](./PLAN.md), [PI-SETUP.md](./PI-SETUP.md), and [WIRING.md](./WIRING.md).

> 🎯 **All of this runs with no payphone attached and nothing new purchased.** The point is to
> retire software risk *before* spending money on parts.

## Layout
| Path | What it is |
|------|------------|
| `src/payphone/dial_decoder.py` | Rotary pulse → digits. Pure logic, no GPIO. |
| `src/payphone/pulse_synth.py` | Synthetic pulse trains (shared by tests **and** the bench rig). |
| `src/payphone/gv_selectors.py` | **Every Google Voice DOM selector**, isolated for cheap repair. |
| `tools/gvcall.py` | Google Voice call control CLI: `probe / status / dial / answer / hangup / watch`. |
| `tools/gpio_loopback.py` | Bench-tests the decoder on real GPIO using one jumper wire. |
| `tools/gpio_probe.py` | Turns the Pi into a logic analyzer for tracing dial/hook contacts. |
| `tests/` | Stdlib `unittest` — runs anywhere, no pip installs. |

## Running the tests
```bash
python -m unittest discover -s tests -v
```
23 tests cover every digit, the `10 pulses = 0` rule, contact bounce, 8–11pps timing drift,
edge jitter, digit separation, and misdial handling.

---

## 1. Decoder bench test (`sw-dial-decoder`)
Proves the decoder against **real GPIO timing** with no payphone. Cost: one jumper wire.

```
Pi GPIO 17 (out) ---- jumper ---- Pi GPIO 27 (in)
```

```bash
python3 tools/gpio_loopback.py                # dial 5551234567
python3 tools/gpio_loopback.py --number 0     # worst case — ten pulses
python3 tools/gpio_loopback.py --bounce       # dirty contacts
```

It replays the *same* waveform the unit tests use onto a real pin and decodes it back, so a pass
means the logic survives real scheduling jitter — not just idealised timestamps.

Convention: **HIGH = contact closed** (loop intact), **LOW = pulse** (open).

---

## 2. Google Voice call control (`sw-call-control`)
⚠️ **The project's biggest unknown.** A human can place a GV call in Chromium; this proves a
*script* can.

### Why attach instead of launch
Playwright ships **no prebuilt ARM Chromium**, so `playwright install` will not give you a working
browser on a Pi. Instead we attach to the *system* Chromium over the DevTools Protocol — which also
reuses your existing Google login.

```bash
sudo apt install -y chromium python3-pip
pip3 install --break-system-packages playwright
# do NOT run `playwright install`
```

Start Chromium with the debug port:
```bash
chromium --remote-debugging-port=9222 \
         --user-data-dir=$HOME/.config/payphone-chromium \
         https://voice.google.com/u/0/calls
```

### Use it
```bash
python3 tools/gvcall.py probe               # ← RUN THIS FIRST
python3 tools/gvcall.py status              # idle | ringing | in-call
python3 tools/gvcall.py dial 5551234567
python3 tools/gvcall.py hangup
python3 tools/gvcall.py answer
python3 tools/gvcall.py watch               # streams JSON state events
```

### Expect to fix selectors — that's by design
Google Voice is a private, obfuscated, unstable web app. The selectors in `gv_selectors.py` are
**unverified starting points**. `probe` dumps every visible button with its `aria-label` and text so
you can paste the real values into that one file. Selectors prefer `aria-label`/`role` because
Google maintains those for accessibility, so they rot far slower than class names.

**This is the known structural weakness of the V2 design** (see decision D3): we drive a web UI
Google can change without notice. Keeping all selectors in one file is the mitigation.

### `watch` feeds the bell
`watch` emits `{"event":"state","state":"ringing"}` on an inbound call. That event is what will
eventually drive the ring cadence (`sw-ring-cadence`) and then the ⚠️ ~90V ring generator's
**Inhibit** line — so the whole inbound path can be built and tested before any high-voltage
hardware exists.

### Troubleshooting

**`Missing X server or $DISPLAY` when launching Chromium over SSH.**
Chromium needs a desktop session; an SSH shell has none. Easiest fix: run the launch command from a
terminal **inside the VNC desktop**. You have to sign into Google Voice in that window anyway.

To launch it from SSH instead, first detect the session type:
```bash
ls /run/user/$(id -u)/wayland-0 2>/dev/null && echo WAYLAND || echo X11
```
X11:
```bash
export DISPLAY=:0
export XAUTHORITY=$HOME/.Xauthority
```
Wayland (Bookworm default on newer Pis):
```bash
export XDG_RUNTIME_DIR=/run/user/$(id -u)
export WAYLAND_DISPLAY=wayland-0
```
…then run the `chromium --remote-debugging-port=9222 …` command. The window appears on the VNC
desktop. Confirm the port is live with:
```bash
curl -s http://localhost:9222/json/version | head -3
```
`gvcall.py` itself can then be run over SSH — it only talks to the debug port.

> ⚠️ **Don't reach for `--headless` to dodge this.** It avoids the display error but the finished
> phone needs real WebRTC audio through the USB sound card, and Google sign-in is painful headless.
> Keep Chromium on the real desktop; `sw-autostart` will launch it unattended later.

---

## Safety
> ⚠️ The bell ring circuit runs at **~90V AC / 20Hz — shock hazard.** Nothing in this directory
> touches high voltage: the Pi only ever drives a **low-voltage logic line** into an opto-isolator,
> which gates the ring generator. Keep it that way — never wire a Pi GPIO to the ring circuit.
