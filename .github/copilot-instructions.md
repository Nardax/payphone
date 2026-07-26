# Copilot instructions for `pay-phone`

## What this repository is
This is a **documentation / planning repository**, not a software project. It holds the design and
task plan for a hardware build: converting a vintage **Automatic Electric 3-slot rotary payphone**
into a working phone over **Wi-Fi + Google Voice** with **no landline, no cell/SIM line, and no
monthly bills**. There is no application code, and therefore **no build, test, or lint commands** —
do not invent tooling or CI. Work here means editing Markdown and keeping the plan coherent.

## The three documents and how they relate
- **`README.md`** — one-page index/overview and the entry point. Keep it short.
- **`docs/PLAN.md`** — the authoritative design. It is structured as **Option A ($0/month)** with two
  mutually exclusive build variants:
  - **Version 1 — Smartphone brain** (spare Android running the official Google Voice app).
  - **Version 2 — Raspberry Pi brain** (unofficial Google Voice bridge/softphone).
  Content common to both lives in **"Shared concepts"**; version-specific content lives under each
  version's own section. Preserve this shared-vs-version split when editing.
- **`docs/TASKS.md`** — a checklist mirror of the plan: **Shared prep → choose a version → that
  version's track → Acceptance**, plus a **Decision log** table (IDs `D1`–`D6`).

## Core design constraints (do not violate when editing the plan)
These come directly from the project owner and shape every recommendation:
- No landline, no dedicated cell/SIM line; calling rides on **Wi-Fi + Google Voice**.
- **$0/month** — this is why the plan avoids paid SIP DIDs. Google Voice gives no SIP credentials,
  so a device that already runs Google Voice acts as the phone's "brain." Don't reintroduce a paid
  SIP/ATA path as the primary design.
- The **authentic rotary dial must work** and the **original bell must physically ring** on incoming
  calls; the handset must have real audio. Any design must still satisfy these four jobs: **audio,
  hook switch (on/off-hook), rotary dialing, and bell/ring.**

## Conventions specific to this repo
- **All diagrams must be Mermaid** (```mermaid fenced blocks) so they render in the browser /
  GitHub. Do not use ASCII-art diagrams.
- **All plans and docs live in the repository, never only in the session.** Any plan, task list,
  design note, or decision record must be written to a committed file in this repo (e.g.
  `docs/PLAN.md`, `docs/TASKS.md`). Do not leave plans solely in the Copilot session folder or the session
  todo database — the session store may be used as a working mirror, but the repo files are the
  source of truth and must be created/updated so the work persists across sessions.
- **Keep the three docs and the task IDs in sync.** Every task has a stable **kebab-case ID** (e.g.
  `build-dial-reader`, `v1-dial-automation`, `v2-pi-bridge`). The same IDs appear in `docs/PLAN.md`'s
  todo list, in `docs/TASKS.md`, and in the Copilot session todo database. When you add, rename, or
  reorder a task, update all places and its **dependency links** (`→ depends-on`).
- **Version prefixes:** shared tasks are unprefixed; Version 1 tasks start with `v1-`; Version 2
  tasks with `v2-`. Maintain this so the two tracks stay cleanly separable.
- **Decisions are tracked by ID** (`D1`–`D6`) in the `docs/TASKS.md` decision log. Reference decisions by
  their ID in prose rather than restating the options; update the log when a decision is made.
- **Safety callout is mandatory:** the bell ring circuit runs at **~90V AC** (shock hazard) and the
  microcontroller logic must stay isolated from it. Keep this warning present wherever ringing is
  discussed; never quietly drop it.
- This is a decision-support/plan repo: when the owner asks technical questions, **explain tradeoffs
  and update the plan**, don't write production code.

<!-- mermaid-ai-skills:start -->
## Mermaid Diagrams

When the user asks to create, edit, or visualize a diagram, follow the
instructions in `.github/instructions/mermaid.instructions.md`.
<!-- mermaid-ai-skills:end -->
