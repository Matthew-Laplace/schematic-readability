# Attribution

The rules in this skill were compared against, and in part informed by, the
following public projects during a survey on **2026-10-04**. Each entry lists
what was taken and how strongly it is evidenced.

**No source code from any of these projects is redistributed in this
repository.** What is carried over is described below: mechanisms, formula
structures, numeric constants, and rule text that has been rewritten for the
target tool. Where a project's licence would not permit code reuse, only its
published ideas are described.

## Evidence Levels Used Above

- `[verified]` - read line by line in the upstream source during the survey
- `[read]` - read in upstream prose documentation
- `[reported]` - reported by a parallel survey pass, not independently verified

## Direct Influences

| Project | Licence | What was carried over | Level |
|---|---|---|---|
| [oaslananka/kicad-mcp-pro](https://github.com/oaslananka/kicad-mcp-pro) | MIT | The **readability score formula** (`score = clamp(100 - sum(min(category_penalty, 40)), 0, 100)`), the original weight table and category grouping, the off-grid test shape, overlap-area thresholds, the estimated text-box formula, density-imbalance and font-mode checks, and the connection-signature algorithm in geometric form | `[verified]` |
| [Arcadia-1/virtuoso-bridge-lite](https://github.com/Arcadia-1/virtuoso-bridge-lite) | MIT | The two-tier hard/soft constraint model with structured diagnostics, planning-step defaults, row separation, dedicated pin column, output-stage shift, differential-pair symmetry constraint, readback comparison fields and tolerance, and the label height default | `[verified]` |
| [deanyou/virtuoso-cli](https://github.com/deanyou/virtuoso-cli) | MIT | Independent confirmation that the schematic grid quantum is `0.0625` units, and the split between automatic and exact-coordinate wire commands | `[verified]` |
| [KwantaeKim/cdl_gen](https://github.com/KwantaeKim/cdl_gen) | MIT | The generator-versus-hand-edit coexistence protocol: hand edits are snapshotted into a separate extension block that takes precedence over the generated block, and deleting it restores generated output | `[verified]` |
| [eelab-dev/EEschematic](https://github.com/eelab-dev/EEschematic) | MIT | Analog-structure placement conventions (current mirror, differential pair, cascode pair, diode-connected device, single current source), wire-avoidance rules expressed as extension points, and the overlap/spacing triggers used in its prompts | `[read]` |
| [Keitark/pcba-design-skills](https://github.com/Keitark/pcba-design-skills) | MIT | The visual audit checklist structure, drawing-hygiene rules (no wires under symbols or text, no ambiguous through-pin routing, no four-way crossings, no label stacking), and the exported-netlist connectivity comparison model | `[reported]` |
| [kh6570/HAbedini-qspice-mcp](https://github.com/kh6570/HAbedini-qspice-mcp) | MIT | Text-upright normalisation as a side effect of moving a part, collision boxes that include reference and value text margins, and connection-preserving moves with explicit rewiring counts | `[read]` |
| [404elf/ltspice-codex-skill](https://github.com/404elf/ltspice-codex-skill) | *no licence file* | Density-driven annotation downgrade: hide eligible passive value text and move values to a parameter block, while keeping sources and active-device model names visible | `[read]` |
| [faisal-shah/agent-skills](https://github.com/faisal-shah/agent-skills) | MIT | Systematic label-overlap countermeasures, quantified spacing and scale tables, the ground-symbol count rule, the exact/abstraction/presentation mode gate, and the coverage-manifest idea | `[read]` |
| [RyanWillie/Volt](https://github.com/RyanWillie/Volt) | Apache-2.0 | The requirement to inspect the rendered drawing rather than trust diagnostics, and an eight-point visual quality rubric | `[read]` |
| [DeconBear/vibe-analog](https://github.com/DeconBear/vibe-analog) | *no licence file* | Partition thresholds, per-page scoring that takes the minimum rather than the mean, and the idea of geometry/readability reports emitted alongside a render with a regression corpus | `[reported]` |
| [aidangoettsch/asg](https://github.com/aidangoettsch/asg) | MIT | Constraint-weighted iteration with early stop and rollback to peak, longest-path column assignment, barycentre vertical ordering, pin-mirror crossing reduction, bounding-box detour routing, and spatial bin pruning | `[reported]` |

## Ideas Only, No Code

| Project | Licence | Note |
|---|---|---|
| [RTimothyEdwards/XCircuit](https://github.com/RTimothyEdwards/XCircuit) | **GPL-2.0** | Only its published routing cost *structure* is described in `references/layout-algorithms.md` - congestion weighting, bend cost, and a near-saturation penalty. **No GPL code, and no GPL source text, is copied or adapted into this repository.** If you intend to reuse its implementation, review the licence first. |

## Additional Sources Consulted

These informed the cross-tool comparison but contributed no rule text:

- [eclipse-elk/elk](https://github.com/eclipse-elk/elk) and
  [kieler/elkjs](https://github.com/kieler/elkjs) - layered crossing
  minimisation, orthogonal routing, port-side constraints.
- [nturley/netlistsvg](https://github.com/nturley/netlistsvg) - skin-based
  rendering over a layout engine; its analog skin has no MOSFET symbol, which is
  recorded as a limitation rather than a feature.
- [devbisme/skidl](https://github.com/devbisme/skidl) - autoplacement, switchbox
  routing, and pin snapping.
- [KiCad/kicad-library-utils](https://github.com/KiCad/kicad-library-utils) -
  the KiCad Library Convention rule implementations used as a model for
  scriptable lint checks.

## Licence Notes

Two surveyed projects publish **no licence file**: `404elf/ltspice-codex-skill`
and `DeconBear/vibe-analog`. Their mechanisms are described here at the level of
idea and threshold only; no code was copied from either. If you plan to reuse
their code rather than their ideas, establish the licensing position first.

Where a rule in this repository was calibrated for the target tool rather than
taken from a source, it is marked `[calibrated]` and should be treated as a
tunable starting point. Do not read a calibrated value as an upstream fact.
