# Task Tracker — Rotary Payphone $0/Month Build

Companion to [PLAN.md](./PLAN.md). Check items off as you complete them. `→` shows dependencies
(do those first). Structure: **Shared prep → choose a version → that version's track → acceptance.**

## Shared prep
- [x] **choose-version** — Choosing the build version → _(none)_ ✅ **Chosen: V2 (Raspberry Pi).**
  Decide V1 (Android + official Google Voice app; reliable, some UI-automation glue) vs V2
  (Raspberry Pi + unofficial GV bridge; scriptable but may break). *Decision D1.*
- [x] **setup-gv** — Setting up the free Google Voice number → _(none)_ ✅ **Done (number exists).**
  Create/confirm a free Google Voice US number (free US/Canada calls + texts, $0/month).
- [ ] **acquire-shared-hw** — Acquiring shared hardware → _(none)_
  ESP32, ~90V AC ring generator module + driver, opto-couplers, handset audio adapter, and bench
  tools (multimeter, soldering kit, spare handset cord, wire, heat-shrink).
- [ ] **reverse-wiring** — Reverse-engineering payphone wiring → _(none)_
  Trace the Automatic Electric 3-slot internals: handset transmitter/receiver, hook switch, rotary
  dial pulse + off-normal contacts, ringer coil/capacitor, coin relay connections.
- [ ] **rewire-signals** — Rewiring payphone to clean signals → reverse-wiring
  Rewire handset, hook switch, dial, and ringer to clean accessible signals; bypass the coin mech.
- [ ] **build-dial-reader** — Building ESP32 rotary pulse reader → acquire-shared-hw, rewire-signals
  Count rotary pulses (1–10, 10=0), detect end-of-digit by inter-digit pause, opto-isolate from
  line voltage. Bench test every digit incl. "0". *Decision D6.*
- [ ] **wire-bell** — Wiring the bell ring generator → acquire-shared-hw, rewire-signals
  Drive the original ringer with a ~90V AC 20Hz generator switched by the ESP32; tune ringer
  capacitor. **SHOCK HAZARD — isolate logic.** *Decision D4.*

## Version 1 — Smartphone brain (recommended)
> ⏭️ **Not selected** — D1 chose V2 (Raspberry Pi). This track is retained for reference only.

- [ ] **v1-prep-phone** — Preparing the smartphone brain → choose-version, setup-gv
  Spare Android with Google Voice app, always-on Wi-Fi + charger.
- [ ] **v1-audio** — Routing handset audio → rewire-signals, v1-prep-phone
  Handset mic/earpiece via USB or Bluetooth audio adapter; verify clean two-way audio.
- [ ] **v1-dial-automation** — Implementing dial automation → build-dial-reader, v1-prep-phone
  ESP32 injects the dialed number + call action into the app via Bluetooth-HID or ADB. *Decision D2.*
- [ ] **v1-hook-ring** — Wiring hook + incoming detection → v1-prep-phone, wire-bell
  Hook switch → answer/hang-up in app; incoming-call detection (Tasker/MacroDroid/ADB) → ESP32 fires bell.

## Version 2 — Raspberry Pi brain
- [x] **v2-pi-bridge** — Setting up Pi + GV bridge → choose-version, setup-gv ✅ **Done — validated call on Pi 3B.**
  Pi + unofficial GV bridge/softphone (self-hosted connector, or Asterisk + GV connector); verify
  inbound + outbound. *Decision D3.*
- [ ] **v2-audio** — Routing handset audio → rewire-signals, v2-pi-bridge
  Handset mic/earpiece via USB audio dongle; verify clean two-way audio.
- [ ] **v2-dial-hook** — Wiring dial + hook to GPIO → rewire-signals, v2-pi-bridge
  Rotary dial + hook to Pi GPIO (optionally via ESP32); script dial/answer/hang-up through the bridge.
- [ ] **v2-incoming-bell** — Wiring incoming call to bell → v2-pi-bridge, wire-bell
  Bridge incoming-call event → Pi GPIO → fires ring generator → bell.

## Acceptance
- [ ] **acceptance-test** — Full acceptance test and documentation → acquire-shared-hw
  End-to-end: outbound rotary dialing connects; inbound GV call rings the bell and answers with the
  handset. Document final build, wiring, and firmware/scripts.
- [ ] **coin-gate** — _(optional)_ Coin-drop dial-tone gate → acceptance-test
  Wire the coin-drop switch so inserting a coin unlocks dial tone before dialing.

## Decision log
| ID | Decision | Options | Chosen |
|----|----------|---------|--------|
| D1 | Build version | V1 smartphone / V2 Raspberry Pi | **V2 Raspberry Pi** |
| D2 | Dial automation (V1) | Bluetooth-HID / ADB | _n/a (V1 not selected)_ |
| D3 | GV bridge (V2) | Self-hosted connector / Asterisk + GV connector | **GV web app in Chromium (WebRTC)** — ✅ validated on Pi 3B |
| D4 | Ring generator | Off-the-shelf ~90V module / salvaged generator | **Off-the-shelf ~90V module** |
| D5 | Handset transmitter | Original carbon mic / electret + bias | **Electret + bias** |
| D6 | Dial reader | ESP32 / direct Pi GPIO (V2) | **Direct Pi GPIO** _(ESP32 fallback)_ |
| D7 | Analog BT gateway (Cell2Jack / XLink BT) | Use as all-in-one FXS gateway / discrete DIY build | **❌ Rejected — discrete DIY build** (HFP `ATD` dials the carrier, not Google Voice; fails SIM-less) |
