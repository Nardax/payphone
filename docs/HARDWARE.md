# Hardware — Bill of Materials (Version 2, Raspberry Pi brain)

Companion to [PLAN.md](./PLAN.md) and [TASKS.md](./TASKS.md). This is the parts list for the
**Version 2 (Raspberry Pi)** build chosen in decision **D1**. All electronics mount **concealed
inside the payphone shell** — the phone must look and behave like an authentic landline.

> ⚠️ **Safety:** the bell ring circuit runs at **~90V AC / 20Hz** — treat it as a **shock hazard**.
> Never power the Raspberry Pi from any high-voltage rail, and keep all microcontroller/GPIO logic
> **opto-isolated** from the line/ring voltage.

## Buy-order strategy — de-risk before you spend
Do **not** order the ring generator and handset-interface parts until the **GV bridge spike**
(`v2-pi-bridge`) proves inbound + outbound calling works on the Pi with a plain USB headset. The
unofficial Google Voice bridge (decision **D3**) is the biggest unknown; validate it first, then buy
the rest. A cheap USB headset for that spike is the only up-front purchase.

## The four jobs → the parts that solve them
| Job | Subsystem | Key parts |
|-----|-----------|-----------|
| Brain + calling | Raspberry Pi + GV bridge | Pi 4, PSU, microSD |
| Audio | Handset ↔ Pi | USB audio adapter, electret mic |
| Dialing + hook | Rotary dial/hook → Pi GPIO | Opto-isolators, resistors |
| Ring | ~90V bell | Ring-generator module, driver relay |

## 1. Brain (Raspberry Pi)
| Item | Notes / suggested spec | Qty |
|------|------------------------|-----|
| Raspberry Pi (3B or newer) | A **Pi 3 Model B is sufficient** to run the GV bridge/softphone headless (SSH). Using one you already own = **$0**. If buying new, a **Pi 4 is the value pick** — a Pi 5 also works but costs more, needs a 5V/5A USB-C PD supply, and wants active cooling, with no benefit for this light workload. | 1 |
| Power supply | Match the board: **Pi 3B → micro-USB 5V/2.5A**; Pi 4 → USB-C 5V/3A; Pi 5 → USB-C 5V/5A (27W) PD | 1 |
| microSD card (32GB) | A2/Class-10; holds OS + bridge software | 1 |
| Pi case | Low-profile so it hides inside the shell | 1 |

## 2. Handset audio (D5 — electret swap)
| Item | Notes | Qty |
|------|-------|-----|
| USB sound card — **dual-jack** (separate mic-in + headphone-out) | **Required** — the Pi 3B has no mic and its 3.5mm jack is output-only. Get **separate 3.5mm jacks** (not a single combined TRRS) so the handset mic + earpiece wire independently. Doubles as the test-call device today. | 1 |
| Electret microphone capsule(s) | Replaces the original carbon transmitter for clean audio; USB card supplies bias. Buy a multipack. *(D5)* | 1+ |
| 3.5mm pigtail cables / screw-terminal breakout | Splice the handset mic + earpiece wires onto the sound card's two jacks | 2 |
| Coupling/attenuation parts | Coupling capacitor for the mic + series resistor to tame the higher-impedance earpiece (resistor/cap assortment kit) | as needed |
| (Optional) original carbon mic | Keep on hand as an authenticity fallback (needs a bias network) | — |

## 3. Dial + hook sensing (D6 — direct Pi GPIO, opto-isolated)
| Item | Notes | Qty |
|------|-------|-----|
| Opto-isolators (e.g., PC817) | Isolate dial-pulse + hook contacts from Pi GPIO | 2–4 |
| Resistors (pull-ups, current-limit) | Assorted; size for the opto LED + GPIO pull-ups | pack |
| Perfboard / protoboard | Mount the sensing + driver circuits | 1 |
| Screw terminals / JST connectors | Clean, serviceable connections to the phone's contacts | assorted |

## 4. Ring circuit — ⚠ ~90V AC (D4 — off-the-shelf module)
| Item | Notes | Qty |
|------|-------|-----|
| Telephone ring-generator module | Produces ~90V AC ~20Hz to strike the original bell | 1 |
| Driver relay or opto-driver + transistor | Pi GPIO switches the ring generator (logic stays isolated) | 1 |
| Flyback diode | Protects the driver when switching the coil/relay | 1 |
| Series ringer capacitor | Tune so the bell strikes reliably (match the ringer coil) | 1 |

## 5. Wiring, mounting & tools
| Item | Notes |
|------|-------|
| Hookup wire, Dupont/JST leads | Interconnects |
| Ferrules, heat-shrink | Clean, insulated terminations |
| Standoffs / mounting hardware | Secure the Pi + boards concealed inside the shell |
| Multimeter | Trace wiring, verify continuity/voltage (never probe ring voltage live) |
| Soldering kit, wire strippers | Assembly |
| Spare handset cord | In case the original is brittle |
| USB headset | **Buy first** — validates the GV bridge before any wiring |

## Shopping checklist
Buy in two phases so the risky GV bridge is proven before you spend on the rest.

### Phase 1 — buy first (prove the GV bridge)
- [ ] Raspberry Pi (3B or newer — a **Pi 3 Model B works**; use one you own for $0. Buying new? **Pi 4 is the value pick**; a Pi 5 works but costs/draws more for no gain here)
- [ ] Power supply to match (Pi 3B → micro-USB 5V/2.5A · Pi 4 → USB-C 5V/3A · Pi 5 → USB-C 5V/5A PD)
- [ ] microSD card (32GB, A2/Class-10)
- [ ] Pi case (low-profile)
- [ ] USB headset (for the bridge spike)

### Phase 2 — buy after the bridge spike passes
**Handset audio (D5)**
- [ ] USB sound card — **dual-jack** (separate mic-in + headphone-out, not single TRRS)
- [ ] Electret microphone capsule(s) — multipack
- [ ] 3.5mm pigtail cables / screw-terminal breakout ×2
- [ ] Resistor + capacitor assortment (mic coupling cap + earpiece series resistor)

**Dial + hook sensing (D6)**
- [ ] Opto-isolators (PC817 or similar) ×2–4
- [ ] Assorted resistors (pull-ups, current-limit)
- [ ] Perfboard / protoboard
- [ ] Screw terminals / JST-Dupont connectors

**Ring circuit — ⚠ ~90V AC (D4)**
- [ ] Telephone ring-generator module (~90V AC 20Hz)
- [ ] Driver relay or opto-driver + transistor
- [ ] Flyback diode
- [ ] Series ringer capacitor (tune the bell)

**Wiring, mounting & tools**
- [ ] Hookup wire + Dupont/JST leads
- [ ] Ferrules + heat-shrink
- [ ] Standoffs / mounting hardware
- [ ] Multimeter
- [ ] Soldering kit + wire strippers
- [ ] Spare handset cord

## Related decisions
See the [decision log](./TASKS.md#decision-log): **D1** V2 Raspberry Pi · **D3** self-hosted GV
bridge (pending spike) · **D4** off-the-shelf ring module · **D5** electret + bias · **D6** direct
Pi GPIO.
