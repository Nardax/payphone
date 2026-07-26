# Total Cost of Ownership — 5-year comparison

Honest cost comparison of every path evaluated for this build. Companion to [PLAN.md](./PLAN.md),
[SHOPPING-LIST.md](./SHOPPING-LIST.md), and the decision log in [TASKS.md](./TASKS.md).

> 💡 **"$0/month" means no *service* bill — not zero cost.** Parts and electricity are real. This
> page exists so the $0/month constraint is judged on total cost, not on the monthly line alone.

## Costing rules
- **Marginal cost only.** Hardware already owned is a **sunk cost and excluded**: the Raspberry Pi 3B,
  32GB card, Pi power supply, and the **UniFi console** (already deployed on this network).
- **Electricity at $0.17/kWh**, always-on, 24×7. Formula: `W × 24 × 365 ÷ 1000 × $0.17`.
- **5-year horizon.** Long enough for subscriptions to dominate, short enough to be realistic.
- Prices are US retail as researched July 2026 and will drift.

---

## Headline comparison

| Path | Parts | Subscription (5yr) | Power (5yr) | **5-year TCO** | Reliability |
|------|------:|------:|------:|------:|---|
| **A — Pi + Chromium** ✅ *validated* | $163 | $0 | $37 | **$200** | 🟢 High — official GV web client |
| **B — Cell2Jack + Android** | $80 | $0 | $15 | **$95** | 🔴 Very low — likely can't dial out |
| **C — UniFi Talk + UT-ATA** | $139 | **$599** | $19 | **$757** | 🟡 High service, but **can't reach GV** |
| **D — Used OBi200 + GV** | $110 | $0 | $19 | **$129** | 🔴 Low — EOL hardware, unofficial firmware |
| **E — HT801 V2 + paid SIP DID** | $50 | $180 | $19 | **$249** | 🟢 Highest — fully supported, maintained |

Power draw assumptions: Pi 3B 3.5W + ring generator idle 1.5W; Android charging 2.0W; ATA 2.5W.

---

## The two findings that matter

### 1. UniFi Talk is out — and not mainly because of cost
UniFi Talk's own calling service is **~$9.99/month per number** (Plus) or ~$24.99 (Pro) — **$599 over
five years**, the most expensive option here by 3×. But cost isn't even the disqualifier:

- The **UT-ATA ($99) is not a generic SIP ATA.** It must be adopted and managed by the Talk
  application; there's no standalone SIP-registration mode to point at Asterisk or anything else.
- Talk *does* support **bring-your-own SIP trunks** — which sounds like the escape hatch, but
  **Google Voice supplies no SIP trunk**, so there is nothing to bring. This is the same wall that
  rules out every ATA path.
- Ubiquiti **publishes no ring voltage or REN** for the UT-ATA, so it can't be responsibly promised
  to strike a payphone gong.

Your console being already-owned removes ~$112 of 5-year electricity from this path, but it doesn't
fix any of the three problems above. **Verdict: dead end for this project.** Recorded as **D8**.

### 2. The DIY "$0/month" path saves less than it appears
Path A costs **$200** over five years. Path E — a supported Grandstream HT801 V2 with a real paid SIP
number — costs **$249**. That is a **$49 difference over five years, about $0.82/month**, in exchange
for dropping the DIY high-voltage ring circuit entirely and getting a maintained, vendor-supported
system.

Notably the **HT801 V2 exposes an "Enable Pulse Dialing" option** and is rated **5 REN**, so it may
drive the rotary dial *and* the bell with no converter and no DIY electronics at all.

This does **not** mean we should switch — the $0/month constraint and the hands-on build are the
point of the project. But it does mean the DIY path should be chosen for **authenticity and control,
not for savings**, because the savings are roughly a dollar a month.

---

## Risk-adjusted notes per path

- **A — Pi + Chromium (current plan).** Only path already **proven with a real call**. Weakness: it
  drives the GV *web app*, so a Google UI change can break automation, and it needs the ⚠️ ~70–90V AC
  ring circuit built by hand. Highest labor.
- **B — Cell2Jack + Android.** Cheapest on paper and the numbers flatter it, but it is the **least
  likely to work at all**: Bluetooth HFP dialing routes to the native carrier dialer, not Google
  Voice, so a SIM-less phone likely cannot dial out. Assumes a spare Android at $0. See **D7**.
- **C — UniFi Talk + UT-ATA.** Most expensive and still cannot reach Google Voice. See **D8**.
- **D — Used OBi200.** Historically *the* free rotary-phone answer and still the best-documented
  ringer (**55–85 Vrms, 5 REN**). But HP ended support **Dec 2023** and shut the OBiTALK provisioning
  portal **Oct 2024**; new setup requires **unofficial community firmware** on discontinued hardware,
  and a factory reset could brick the configuration permanently.
- **E — HT801 V2 + paid SIP DID.** Violates the $0/month rule (~$1.50–3/mo DID plus usage) but is the
  only path that is fully supported end-to-end. Included as the honest baseline.

---

## Optional: labor
Excluded from the headline table because it's not a cash cost — but at any nonzero hourly value it
dominates every other number.

| Path | Rough build time | @ $25/hr |
|------|---:|---:|
| A — Pi + Chromium | 15–25 hrs (tracing, soldering, HV ring circuit, GPIO scripting) | $375–625 |
| E — HT801 V2 + SIP | 3–5 hrs (mostly configuration) | $75–125 |

If labor is priced in, Path E wins decisively. If the build **is** the hobby, labor is the point and
this table is irrelevant. Both readings are legitimate — hence keeping it separate.

---

## Conclusion
**Stay on Path A.** It's validated, meets the $0/month constraint, and at **$200 over five years** is
the cheapest option that actually works. Path C (UniFi) is rejected as **D8**. Path D is the only
credible ATA alternative and is worth knowing about **only** if the DIY ring circuit defeats us —
budget ~$129 and accept EOL-hardware risk.
