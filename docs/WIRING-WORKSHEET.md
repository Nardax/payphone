# Wiring Worksheet — fill this in while tracing (`reverse-wiring`)

Printable/fill-in companion to [WIRING.md](./WIRING.md). **Record measurements here as you go** —
this worksheet becomes the source of truth for every later wiring step, and it's what saves you from
re-tracing the whole phone after a break in the work.

> ⚠️ **Before you start:** nothing connected to a phone line, nothing powered, and **no ring
> generator connected**. The ~90V AC ring circuit is a shock hazard and will destroy a Pi GPIO.
> Tracing is safe precisely *because* nothing is energized — keep it that way.

> 🎨 **Wire colors vary** across AE production runs and prior repairs. **Trust the meter, not the
> color.** Record what you actually measure.

---

## 0. Before opening
| Item | Record |
|------|--------|
| Photos taken of internals (before touching anything) | ☐ yes |
| Any wires already cut / previously modified? | |
| Model / date stamps found inside | |

---

## 1. Handset
Set meter to **ohms**.

| Pair | Terminal / wire color | Reading (Ω) | Reacts to tapping? | Conclusion |
|------|----------------------|-------------|--------------------|------------|
| A | | | ☐ yes ☐ no | |
| B | | | ☐ yes ☐ no | |

- **Transmitter (carbon mic):** low and *variable* — reading jumps/scratches when tapped.
- **Receiver (earpiece):** steady, typically a few hundred ohms.

> 💡 A dead-open transmitter is common on carbon mics. If pair A reads open and won't respond,
> that's the known failure that decision **D5** already anticipates — we replace it with an electret.

**Result:** transmitter = ______________  receiver = ______________

---

## 2. Hookswitch
Watch the meter while lifting/lowering the cradle.

| Contact pair | Wire colors | On-hook (handset down) | Off-hook (handset up) | Use for sensing? |
|--------------|-------------|------------------------|-----------------------|------------------|
| | | ☐ closed ☐ open | ☐ closed ☐ open | ☐ |
| | | ☐ closed ☐ open | ☐ closed ☐ open | ☐ |

Pick **one clean pair** that changes reliably. Confirm it on the Pi:

```bash
python3 tools/gpio_probe.py hook --pin 22
```

**Chosen pair:** ______________  **Off-hook =** ☐ closed ☐ open

---

## 3. Rotary dial
The dial has **two** contact sets and telling them apart is the crux of this whole step:

| Contact set | Behavior while dialing "3" |
|-------------|----------------------------|
| **Pulse (interrupter)** | opens/closes **3 times** |
| **Off-normal (shunt)** | stays closed for the **entire rotation**, once |

A multimeter often can't follow 10 pulses/second. Use the Pi instead — it decodes live:

```bash
python3 tools/gpio_probe.py dial --pin 17    # decodes digits
python3 tools/gpio_probe.py edges --pin 17   # raw transitions if unsure
```

| Contact set | Wire colors | Transitions when dialing "3" | Conclusion |
|-------------|-------------|------------------------------|------------|
| | | | ☐ pulse ☐ off-normal |
| | | | ☐ pulse ☐ off-normal |

**Verify the classic gotcha — dial `0`:**

| Dialed | Pulses counted | Decoded digit | Pass? |
|--------|---------------|---------------|-------|
| 1 | | | ☐ |
| 5 | | | ☐ |
| **0** | **should be 10** | **should be 0** | ☐ |
| 9 | | | ☐ |

**Measured pulse rate:** ________ pps  *(8–11 is normal for a worn dial; the decoder handles it)*

**Chosen pulse pair:** ______________

---

## 4. Ringer — ⚠️ do not power yet
| Item | Wire colors | Reading | Notes |
|------|-------------|---------|-------|
| Ringer coil resistance | | ______ Ω | expect ~few hundred Ω – 2kΩ |
| Series capacitor present? | | ☐ yes ☐ no | value if marked: ________ |
| Gongs physically strike freely? | | ☐ yes | check the clapper isn't seized |

> ⚠️ **This is the ~90V AC / 20Hz circuit.** Identify and label it now, but **do not connect any
> generator** until `wire-bell`, and never connect it to a Pi GPIO. The Pi only ever drives the ring
> module's low-voltage **Inhibit** line through an opto-isolator.

---

## 5. Coin mechanism (to bypass)
| Item | Wire colors | Notes |
|------|-------------|-------|
| Coin relay coil | | |
| Coin-drop / trigger switch | | keep for the optional `coin-gate` task |
| Terminals to isolate | | |

---

## 6. Line pair (tip / ring)
| Signal | Wire color | Notes |
|--------|-----------|-------|
| Tip | | often green |
| Ring | | often red |

We do **not** use these for calling — no phone line is involved. Identify them only so you can be
certain they're isolated from everything you connect to the Pi.

---

## 7. Final signal map
Once everything above is filled in, record the four connections that actually matter:

| Job | Payphone contact | Wire color | Pi GPIO | Verified |
|-----|-----------------|------------|---------|----------|
| Hook sense | | | | ☐ |
| Dial pulse | | | | ☐ |
| Ring trigger (to opto → generator Inhibit) | | | | ☐ |
| Handset audio | | | *USB sound card, not GPIO* | ☐ |

**Sign-off:** all four verified on the bench before permanent wiring ☐  Date: ____________
