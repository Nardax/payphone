# Shopping List — Version 2 (Raspberry Pi) build, with part numbers + links

Concrete, buyable version of the [HARDWARE.md](./HARDWARE.md) bill of materials for the payphone
build. Grouped by subsystem, with a recommended part, approximate price, and a link. Companion to
[PLAN.md](./PLAN.md), [WIRING.md](./WIRING.md), and [PI-SETUP.md](./PI-SETUP.md).

> ⚠️ **Safety:** the bell **ring circuit runs at ~90V AC / 20Hz — shock hazard.** Keep Pi/GPIO logic
> **opto-isolated** from it and never power the Pi from any HV rail.

> ℹ️ **Prices/links are approximate (US retailers, subject to change).** Manufacturer part numbers
> (MPNs) are the stable reference — verify the current listing before buying. Commodity items link
> to a search rather than a single listing so the link keeps working.

---

## Already have (no purchase)
| Item | Notes |
|------|-------|
| Raspberry Pi 3 Model B | ✅ owned — validated placing Google Voice calls |
| 32GB microSD card | ✅ owned — Raspberry Pi OS Desktop flashed |
| Micro-USB 5V/2.5A power supply (Pi) | Reuse if you have one; else search "raspberry pi 3 power supply" |

---

## 1. Handset audio (decision D5 — electret)
| Item | Recommended part / MPN | ~Price | Link |
|------|------------------------|--------|------|
| USB sound card (dual-jack: separate mic-in + headphone-out) | **Sabrent AU-MMSA** | ~$8 | [Amazon B00IRVQ0F8](https://www.amazon.com/Sabrent-External-Adapter-Windows-AU-MMSA/dp/B00IRVQ0F8) |
| Electret mic capsule | **CUI/Same Sky CMA-4544PF-W** (DigiKey 102-1721-ND) | ~$1 ea | [DigiKey](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CMA-4544PF-W/1869981) · [Amazon multipack](https://www.amazon.com/s?k=electret+microphone+capsule) |
| 3.5mm pigtail cables / screw-terminal breakout | 3.5mm stereo pigtail or terminal block ×2 | ~$7 | [Amazon](https://www.amazon.com/s?k=3.5mm+stereo+screw+terminal+breakout) |
| Resistor + capacitor assortment | For mic coupling cap + earpiece series resistor | ~$13 | [Amazon](https://www.amazon.com/s?k=resistor+capacitor+assortment+kit) |

## 2. Dial + hook sensing (decision D6 — Pi GPIO, opto-isolated)
| Item | Recommended part / MPN | ~Price | Link |
|------|------------------------|--------|------|
| Opto-isolators | **PC817** (multipack) | ~$7 | [Amazon](https://www.amazon.com/s?k=PC817+optocoupler) |
| Perfboard / prototype board | Double-sided FR4 assortment | ~$9 | [Amazon](https://www.amazon.com/s?k=perfboard+prototype+board) |
| PCB screw terminals / Dupont leads | 2- & 3-pos 2.54mm terminals + jumper leads | ~$8 | [Amazon](https://www.amazon.com/s?k=2.54mm+pcb+screw+terminal+block) |

## 3. Bell / ring circuit — ⚠ ~90V AC (decision D4)
| Item | Recommended part / MPN | ~Price | Link |
|------|------------------------|--------|------|
| Ring-generator module | **MRCS Ringing Generator** (12V DC → 70V AC 20Hz; PowerDsine PCR-SIN03V12F20) — has an **Inhibit** line for GPIO cadence control | ~$42 | [MRCS](https://www.modelrailroadcontrolsystems.com/ringing-generator-module-and-ringer/) |
| ↳ higher-voltage alt (if 70V won't reliably strike the bell) | **Old Phone Shop Ring Booster** (~90V AC) | ~$80+ | [Old Phone Shop](https://www.oldphoneshop.com/products/ring-booster-for-old-vintage-telephones.html) |
| 12V DC supply for the ring module | 12V 1–2A barrel adapter | ~$9 | [Amazon](https://www.amazon.com/s?k=12V+2A+power+supply) |
| Opto-isolated relay module (only if your module lacks an inhibit/logic input) | 1-channel 5V, contacts rated ≥250VAC | ~$7 | [Amazon](https://www.amazon.com/s?k=raspberry+pi+opto+isolated+relay+module) |
| Ringer series capacitor | Reuse the phone's original; spare 0.47–1µF ≥250V film cap | ~$5 | [Amazon](https://www.amazon.com/s?k=0.47uF+250V+film+capacitor) |

> 🔔 **Ring control approach:** the MRCS module's **Inhibit** input lets the Pi GPIO start/stop
> ringing with a **low-voltage logic signal** (drive it through a PC817 opto), so you may **not need
> an HV relay** in the ring path at all — the cleanest, safest option. Use the relay row only if you
> pick a bare generator with no logic input. The exact bell wiring goes in [WIRING.md](./WIRING.md)
> when the `wire-bell` task is built.

## 4. Wiring & mounting
| Item | Recommended part | ~Price | Link |
|------|------------------|--------|------|
| Hookup wire (22 AWG assorted) | Solid + stranded kit | ~$14 | [Amazon](https://www.amazon.com/s?k=22+awg+hookup+wire+kit) |
| Heat-shrink tubing kit | Assorted diameters | ~$8 | [Amazon](https://www.amazon.com/s?k=heat+shrink+tubing+kit) |
| Wire ferrules | Insulated ferrule + crimp kit | ~$18 | [Amazon](https://www.amazon.com/s?k=wire+ferrule+crimp+kit) |
| Standoffs / mounting hardware | M2.5 nylon standoff kit (mount Pi + boards inside shell) | ~$9 | [Amazon](https://www.amazon.com/s?k=M2.5+nylon+standoff+kit) |

## 5. Tools (skip any you own)
| Item | Recommended | ~Price | Link |
|------|-------------|--------|------|
| Digital multimeter | Any auto-ranging DMM | ~$25 | [Amazon](https://www.amazon.com/s?k=digital+multimeter) |
| Soldering iron kit | Temp-controlled + solder | ~$30 | [Amazon](https://www.amazon.com/s?k=soldering+iron+kit) |
| Wire strippers | Self-adjusting or gauged | ~$12 | [Amazon](https://www.amazon.com/s?k=wire+strippers) |
| Spare telephone handset cord | 4-conductor, spade/modular | ~$8 | [Amazon](https://www.amazon.com/s?k=telephone+handset+cord) |

---

## 6. Optional experiment — Cell2Jack shortcut test (decision D7)
**Not part of the build.** D7 rejected analog Bluetooth gateways as the *primary* path, but the
device is cheap enough to be worth a bounded test **if** you'd rather not build the discrete circuit.
It only pays off if it passes both gates below — buy from a **returnable** source.

| Item | Recommended part / MPN | ~Price | Link |
|------|------------------------|--------|------|
| Cell-to-landline BT gateway | **Cell2Jack** | ~$40 | [Amazon B089984QRT](https://www.amazon.com/Cell2jack-Cellphone-Adapter-Receive-landline/dp/B089984QRT) |
| ↳ alt (documents pulse dialing + stronger ring) | **XLink BT HD** | ~$70 | [myxlink.com/bthd](https://myxlink.com/bthd) |

Requires a **spare Android phone** as the brain (reverting D1 to V1) — the Pi cannot be the HFP
source. See the `cell2jack-spike` task in [TASKS.md](./TASKS.md) for the two pass/fail gates.

⚠️ Even if both gates pass, outbound dialing still needs
[SouthJack](https://github.com/aarongress1/southjack) (an unproven, single-device proof of concept
requiring a disabled lock screen) to route HFP dialing into Google Voice. Weigh that maintenance
risk against the ~$115 discrete build.

---

## Rough budget
| Group | Approx. |
|-------|---------|
| Handset audio | ~$30 |
| Dial + hook sensing | ~$24 |
| Bell / ring circuit | ~$60 (MRCS + 12V supply + caps); more if the ~90V booster is needed |
| Wiring & mounting | ~$49 |
| Tools (if none owned) | ~$75 |
| **Total (new, incl. tools)** | **~$240** — or **~$115** in consumables if you already own the tools |

The Pi, card, and calling are **$0/month**; this is the one-time parts spend to make the physical
payphone work. The single long-lead / big-ticket item is the **ring-generator module** — order it
early. Everything else is commodity/next-day.
