# Tool Adapters

The readability doctrine in this Skill is tool-agnostic. This file maps it onto
the tools actually in use, and states plainly where a rule does **not** carry
over.

Read the adapter for the tool in front of you. Do not mix adapters: a coordinate
convention or a scoring constant from one tool is not evidence for another.

## Cadence Virtuoso / OA (primary)

**This is the authoritative adapter.** Everything in `SKILL.md` is written for
it. The other adapters below are narrower.

- Connectivity is established by coincident geometry and the global-net
  convention. A label only *names* a net. `instTerm` binding alone is not
  reviewable.
- Acceptance is two-tier: Save Acceptance Gates (netlist unchanged,
  `schCheck` zero errors and zero warnings) plus the pre-write pin and geometry
  gate. The readability score is advisory and sits below both.
- Grid quantum `0.0625`; compact same-direction external pin banks use `0.125`
  (two quantum steps) where no project override applies.
- Wire style: ordinary thin `line` only. A `type=wide` wire or any non-zero
  `~>width` is a defect. Legacy wide bars are load-bearing - they own the label
  that names the net - so converting them requires the repair pass documented
  in `SKILL.md`.
- `schCheck` warnings are blocking, not advisory. The `Solder dot on cross
  over` warning means a four-branch dotted junction must be split into two
  three-way T junctions.
- Symbol writes need their own authorization. A schematic write is not
  permission to touch a `symbol` view.

## KiCad

`[verified]` from `oaslananka/kicad-mcp-pro`.

- The cosmetic score is a deterministic 0-100 over graded findings with a
  per-category cap; see `readability-scoring.md` for the formula and the
  weight table.
- The safety property worth copying: every cosmetic fixer computes a
  **coordinate-free connectivity signature** before and after and refuses to
  write if it would change. See `readability-rules.md` section 7.1.
- The review loop is score -> dry-run fixer -> apply -> render -> re-score ->
  electrical check, stopping when no fixer applies. This Skill's
  `readability-scoring.md` adapts that loop.
- **Do not copy across:** off-sheet checks, title-block completeness, paper
  extents, footprints, and ERC have no OA counterpart. Diagonal wires are legal
  in KiCad but a diagonal in OA is a warning-bearing defect in the context of a
  routed net.
- Unit caution: the upstream thresholds are millimetres on a KiCad sheet with a
  `1.27 mm` grid. Re-derive for `0.0625`; do not import the numbers.

## LTspice

`[read]` from `404elf/ltspice-codex-skill`.

- Useful mechanism: **density-driven annotation downgrade.** When a sheet has
  at least eight simple top-level passive cards and at least four value strings
  longer than eight characters, switch to compact display - component names on
  the drawing, values moved to a parameter block below it.
- Only eligible passive value windows are hidden; source waveforms and active
  device model names stay visible. This "hide the least informative text only"
  restriction is the transferable rule, not the specific threshold.
- Overlapping symbol bounding boxes block delivery. Crowded node labels may be
  moved along their original wire segments, with each move re-verified and
  recorded.
- Honest limitation stated upstream and worth repeating: text bounds are
  estimates, so a layout pass is not a pixel-perfect visual certificate.

## QSpice

`[read]` from `kh6570/HAbedini-qspice-mcp`.

- **Text-upright normalisation as a side effect of movement.** Moving or
  rotating a part resets its reference and value text to horizontal
  left-to-right reading order by default, with an explicit opt-out. Adopting
  this as default behaviour removes the "wire moved, text left crooked" defect
  class entirely.
- Collision boxes include the reference and value text margin, not just the
  symbol body.
- Moving a wired part preserves attached wire endpoints, junctions, and net
  labels, and reports how many endpoints were rewired. The reporting is the
  valuable part: a silent rewire hides a potential connectivity change.
- Anti-patterns worth reusing verbatim: placing every part at the origin,
  treating a derived simulation copy as the editable master, and disabling
  connection preservation and then forgetting to rewire.

## SPICE Netlist To A Publication Figure

`[read]` from `faisal-shah/agent-skills` `netlist-to-schematic`, which renders
via Circuitikz. Relevant when the deliverable is a standalone figure rather
than an EDA database - a case `SKILL.md` already covers under figure-level
redraw.

- The highest-value rule: **label overlap is the single most common quality
  defect**, and the fix is systematic rather than per-instance - never use the
  default label anchor on a vertical component; place an explicit node at the
  midpoint on the free side.
- Quantified spacing: three units between main-path endpoints, three units of
  height for vertical components, two to two-and-a-half for parasitics, two to
  three units of horizontal gap between parallel branches, extra margin at the
  right edge for callouts.
- Scale table by circuit size: 5-10 components under 20 units wide at
  0.80-0.90 scale; 10-20 at 20-35 units and 0.65-0.80; 20+ at 35+ units and
  0.50-0.65.
- Ground-symbol policy: up to five ground connections may share a bus; sixteen
  or more should use individual ground symbols, because long wires converging
  on one bus turn the drawing into spaghetti.
- **Mode gate:** exact transcription, engineering abstraction, presentation
  simplification, or physical-fixture overlay. Default to exact; any
  abstraction must be annotated on the drawing itself and listed in a coverage
  manifest with component counts, critical nodes, polarity checks, and
  omissions.
- Large circuits: render named sections, and prefer a system-level block
  diagram plus a separate detail drawing over forcing every internal element
  into one image.

Its coverage manifest is a good model for this Skill's delivery report: record
what was drawn, what was summarised, and what was omitted.

## xschem / XCircuit / ASG

Relevant to SPICE-to-schematic generation outside Cadence.

- The original ASG is a C implementation descended from the SPAR work, with
  corner-stitched tile routing and a MOS symbol library
  (`NMOS3` / `PMOS3`), consuming a SPICE deck. A later Python rewrite targets
  xschem / EESchema output with a constraint-weighted iterative solver.
- The Python rewrite is the more portable design; its algorithms are described
  in `layout-algorithms.md`, together with two defects found in it.
- **Licence caution:** XCircuit is GPL-2.0. Read it for algorithm ideas; do not
  copy its code into a permissively licensed skill.

## Standalone Figures - SVG, PDF, PNG, EMF, HTML Canvas

Already governed by `## Figure-Level Redraw Outside OA` in `SKILL.md`, with one
addition worth repeating here because it is the most common failure:

- **Extract the vector source before judging connectivity.** A `pptx`, `docx`,
  or `pdf` usually embeds a `vsdx`, EMF, or SVG with exact segment endpoints.
  Parse it and use those coordinates as evidence. A thumbnail or screenshot is
  never connectivity evidence, and re-examining it is not progress.
- A pin counts as connected only when it is enrolled in the intended net's
  terminal set **and** at least one routed branch actually ends on it, either
  as a terminal endpoint or as a junction lying exactly on that pin. A polyline
  that merely crosses a pin is a defect.
- Declare the authority split before the first edit: a reference sketch governs
  topology, block boundaries, and reading order; an extracted netlist governs
  device identity, sizes, terminal names, and per-device connectivity. If they
  disagree, report the exact difference and ask, rather than resolving it by
  taste.

## Cross-Tool Summary

| Concern | Cadence OA | KiCad | LTspice | QSpice | Circuitikz figure |
|---|---|---|---|---|---|
| Connectivity source | coincident geometry + global net | netlist / geometry signature | netlist | netlist + preserved connections | figure's own net declarations |
| Grid quantum | `0.0625` | `1.27 mm` | tool units | tool units | drawing units |
| Score available | no (this Skill defines one) | yes, `sch_cosmetic_score` | no | no | no |
| Auto text uprighting | no | no | no | **yes** | manual |
| Warning gate | `schCheck` zero warnings | ERC (separate) | layout verdict | - | machine check |
| Label carries connection | **no** | yes | no | no | no |

The single most important column is the last row. Any rule that assumes a label
creates connectivity is false for OA, and mixing such a rule in is the easiest
way to produce a schematic that looks right and is electrically wrong.
