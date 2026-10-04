# Schematic Readability

An agent skill for drawing, reviewing, and repairing electronic schematics that
are **both electrically faithful and actually readable**.

Most schematic automation can prove a drawing is electrically correct. Almost
none can tell you whether a human can read it. This skill closes that gap with a
deterministic readability score, a render-review loop, and a hard rule that
readability work may never change the netlist.

```text
Gate layer  (binary, must all pass)
  netlist unchanged  +  schCheck zero errors and zero warnings
  +  pre-write pin and geometry gate

Score layer (continuous 0-100, advisory)
  readability score with per-category breakdown and a worst_category pointer
```

The gates outrank the score. A high score never excuses a failed gate, and a
clean electrical check does not mean the schematic is readable - that is
precisely why the second layer exists.

## What It Covers

- **Placement grammar** for analog blocks: functional islands, current mirrors,
  differential pairs, cascode stacks, protection networks.
- **Full visual bounds** rather than body-only boxes - symbol body, pin figures,
  pin names, instance name, parameters, power pins, stubs.
- **Symmetry** as an explicit constraint with a caller-supplied axis, never
  inferred from net names.
- **Routing and annotation hygiene**: orthogonal routes, no wires through symbol
  bodies, no ambiguous four-way junctions, consistent label height, clearance
  from text and pins.
- **External interface banks**: pin access points on the symbol border, pin
  figures outside, names inside, a confirmed bank pitch.
- **Connection-signature safety**: compute a connectivity signature before and
  after a cosmetic change and refuse the write if any net changed.
- **Cross-tool adapters** for KiCad, LTspice, QSpice, xschem/XCircuit, and
  standalone SVG/PDF/EMF/HTML figures.

Cadence Virtuoso / OA is the **authoritative adapter**. Rules borrowed from
other tools are marked as such and never silently promoted to OA truth.

## Layout

```
SKILL.md                                        entry point and reference map
README.md                                       this file
ATTRIBUTION.md                                  upstream credits and evidence levels
LICENSE                                         MIT
CALIBRATION.md                                  calibrate the skill for your project
CALIBRATION.ja.md                               the same, in Japanese
CALIBRATION.zh-TW.md                            the same, in Traditional Chinese
references/
  readability-rules.md                          cross-tool rules with evidence grades
  readability-scoring.md                        score model and render-review loop
  layout-algorithms.md                          placement and routing algorithms
  tool-adapters.md                              per-tool mapping and exclusions
  compact-functional-block-style.md             analog island style guide
  hierarchical-mixed-signal-readability.md      hierarchy, pin banks, mixed signal
  review-checklist.md                           pre- and post-generation checklists
scripts/
  validate_spectre_hierarchy_contract.py        producer/consumer contract checker
  test_validate_spectre_hierarchy_contract.py   its tests
  thin_wide_wires.il                            wide-path to thin-line converter
  fixtures/                                     example contract and netlist
```

## Calibrating For Your Project

The shipped values are starting points, not measurements. Several are marked
`[calibrated]` for exactly that reason.

**[Calibrating This Skill For Your Project](CALIBRATION.md)** - also available in
[日本語](CALIBRATION.ja.md) and [繁體中文](CALIBRATION.zh-TW.md) - walks through
the three axes that make the output match your house style:

1. **Exemplar calibration.** Draw a five-transistor OTA with the skill as-is,
   then compare it against one you drew yourself and feed the differences back.
   Repeat until a fresh run reproduces your exemplar's *grammar*.
2. **Grid requirements.** Declare your project's lattice, pin-bank pitch, label
   height, and half-grid policy. Every geometry rule derives from this, so
   settle it first.
3. **Note requirements.** Fix your conventions for in-drawing annotations and
   for the delivery record, so a drawing reads as finished to your reviewers.

## Installing As A Skill

Copy the directory into your agent's skill folder, for example:

```bash
cp -R schematic-readability ~/.codex/skills/cadence-schematic-generation-readability
```

The skill is plain Markdown plus two scripts. There is nothing to build and no
dependency to install. The Python checker uses the standard library only.

## Evidence Grades

Every borrowed rule carries a grade, because a rule copied from another tool is
not evidence that it holds in yours:

| Grade | Meaning |
|---|---|
| `[verified]` | Read line by line in the upstream source during the 2026-10-04 survey |
| `[read]` | Read in upstream prose documentation |
| `[reported]` | Reported by a parallel survey pass; **not independently verified** |
| `[calibrated]` | This skill's own starting value, with no external validation |

The score formula and its weight table are `[verified]`: they were read directly
out of the one upstream project that publishes a deterministic implementation
(see `ATTRIBUTION.md`). Several algorithm constants in
`references/layout-algorithms.md` are `[reported]` - re-check them against the
upstream source before relying on them.

## Honest Limits

- The skill **does not** establish circuit function, simulation correctness,
  DRC/LVS, or signoff. It governs drawing and review only.
- A clean `schCheck` is necessary but never sufficient for readability.
- The readability score is a directional proxy. The upstream implementation it
  is based on states plainly that the **render is the ground truth**, and that a
  score is only a fast way to decide what to fix first.
- Text-extent checks are **estimates**, since schematic databases do not store
  rasterised text boxes. Findings derived from them are marked as estimates.
- Stopping rule: when a full repair pass produces no applicable change, stop -
  even if the score is still below target. The remaining gap needs human
  judgement, not more automated nudging.

## Non-Negotiable Rules

These are the invariants the whole skill is built around:

1. **A readability change must not change the netlist.** Snapshot the
   `(instance, terminal) -> net` mapping before and after and require an exact
   match. If a readability goal cannot be met without moving a terminal to
   another net, stop and report the conflict.
2. **Never save a schematic that is not warning-free.** Floating, dangling, or
   unused wire and label objects are defects to fix, not noise to accept.
3. **An instance-terminal binding alone is not reviewable.** Every terminal
   needs visible geometry or a short stub plus an unambiguous net label, and
   every visible wire must be bound to its real net.
4. **Never exchange terminals for appearance.** Drain, source, gate, and bulk
   assignments are frozen during layout work. A cleaner drawing with an
   unexplained terminal change is a failed result.
5. **A label never creates a connection in a schematic database.** It names a
   net. Connectivity comes from coincident geometry and the global-net
   convention. Any advice of the form "prefer labels over wires" is wrong for
   this target.

## Scope Note

This is a working engineering skill, not a specification. Some rules are dated
because they were confirmed in practice on a specific date, and a few record
measured evidence from real repair passes. Where a rule is project-specific it
says so; do not universalise a project convention into a portable one.

## Licence

MIT - see `LICENSE`. Rules and mechanisms were informed by the public projects
listed in `ATTRIBUTION.md`; no third-party source code is redistributed here.
