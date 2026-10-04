# Readability Scoring And Render-Review Loop

This guide adds a **continuous readability score** on top of this Skill's
existing binary gates. It is the answer to a specific gap: the gates can prove
that a schematic is electrically unchanged and warning-free, but they cannot
distinguish "drawn well" from "drawn badly". A sheet can pass every gate and
still be unreadable.

## Priority Order — Gates Outrank Scores

```
Gate layer (binary, must all pass)
  = netlist unchanged  +  schCheck zero errors and zero warnings
  +  pre-write pin and geometry gate

Score layer (continuous 0-100, advisory)
  = the readability score below
```

A high score never excuses a failed gate, and a gate failure makes the score
meaningless. Conversely, passing every gate does **not** mean the schematic is
readable - that is exactly why this layer exists. Report the two layers
separately and never merge them into one verdict.

## The Score

```
score = clamp( 100 - SUM_over_categories( min(category_penalty, 40) ) , 0 , 100 )
worst_category = argmax(category_penalty)     # before the per-category cap
```

Penalties accumulate **per finding**, so N occurrences of the same defect cost
N times. Each category is capped at `40`, which prevents one flooded category
from zeroing the total and keeps the number informative across mixed defect
profiles. Round to one decimal.

The `40` cap and the accumulation rule are taken from the one upstream
implementation that publishes a deterministic formula
(`oaslananka/kicad-mcp-pro`, `src/kicad_mcp/models/visual_qa.py:992-1022`,
verified 2026-10-04). The **category mapping and the OA-specific codes are
adapted for this Skill**; the KiCad-only codes (title block, off-sheet, paper
edge, footprint, ERC) are deliberately dropped because OA has no such objects.

### Penalty Table

| Code | Penalty | Category | Evidence source |
|---|---|---|---|
| `symbol_overlap` | 15 | geometry | upstream weight |
| `terminal_visually_uncovered` | 15 | connectivity-visibility | calibrated |
| `orphan_wire_no_net` | 15 | wiring | calibrated |
| `wire_through_body` | 12 | geometry | calibrated |
| `text_overlap` | 10 | annotation | upstream weight |
| `label_overlap` | 8 | annotation | upstream weight |
| `four_way_junction` | 8 | wiring | calibrated |
| `different_net_crossing` | 6 | wiring | calibrated |
| `power_pin_sideways` | 6 | orientation | upstream weight |
| `grid_misalignment` | 4 | grid | upstream weight |
| `label_height_inconsistency` | 4 | typography | upstream weight |
| `pin_bank_pitch_deviation` | 4 | interfaces | calibrated |
| `diagonal_wire` | 3 | wiring | upstream weight |
| `dense_label_fanout` | 3 | annotation | upstream weight |
| `island_scatter` | 3 | layout_balance | calibrated |
| `density_imbalance` | 3 | layout_balance | upstream weight |
| `frame_or_note_missing` | 2 | documentation | calibrated |
| `report_missing` | 2 | documentation | calibrated |

Weights marked `upstream weight` come from `COSMETIC_PENALTIES` in the file
above. Weights marked `calibrated` are this Skill's own starting values and
**have not been validated against a corpus**; treat them as a tunable baseline,
not as measured constants. Do not present a calibrated weight as an upstream
fact.

### Category Definitions

| Category | Covers |
|---|---|
| `geometry` | symbol and body overlap, wires routed through symbol bodies |
| `connectivity-visibility` | terminals with no visible wire, stub, or label |
| `wiring` | orphan (`net=nil`) wires, different-net crossings, four-way junctions, diagonals |
| `annotation` | text and label overlap, label crowding |
| `orientation` | sideways power and ground symbols |
| `grid` | off-lattice instance origins, wire endpoints, label anchors, junctions |
| `typography` | mixed label heights for one label class |
| `interfaces` | compact same-direction pin banks deviating from the confirmed pitch |
| `layout_balance` | scattered functional islands, content crowded into one region |
| `documentation` | missing functional frame or note, missing review evidence |

### Thresholds To Reuse

These come from the upstream implementation and are unit-compatible after
rescaling to schematic units. They are **not** this project's grid.

| Quantity | Upstream value | Note |
|---|---|---|
| Grid quantum used by the off-grid check | `1.27 mm` | use the **confirmed project grid** (`0.0625`) instead |
| Off-grid tolerance | `> 0.01` of the grid unit | reuse the shape of the test, not the number |
| Diagonal test | `dx > 0.01` and `dy > 0.01` and length `>= 0.05` | scale to project units |
| Text-overlap minimum area | `1.0 mm²` | scale; below this a graze is legal |
| Symbol-overlap minimum area | `1.0 mm²` | positive width **and** positive height |
| Estimated text box | `width = len * font * 0.66`, `height = font` | bold multiplies width by `1.12` |
| Dense fanout | `>= 6` neighbours within `5 mm` | scale radius |
| Density imbalance | `>= 8` symbols, `<= 1` occupied quadrant or busiest `>= 85%` | 2x2 quadrants |

Both overlap checks require a **positive-area** intersection. Edge-only or
corner-only contact is not overlap and must not be penalised - this matches the
geometry gate in the main Skill, which treats a zero-area touch as legal.

## What OA Can And Cannot Score

Before writing a scorer, classify each check. Do not pretend a render-only
check is scriptable, and do not invent an OA object that does not exist.

| Class | Checks |
|---|---|
| **Scriptable from OA** | off-grid instance origins, wire endpoints, label anchors, junctions; diagonal wires; orphan wires with `net=nil`; pairwise transformed-master BBox intersection; `label~>height` mode; power and ground pin orientation by naming convention; quadrant clustering |
| **Scriptable but not exact** | text and label overlap - OA stores no rasterised text extent, so apply the estimated-box formula above and mark the result an estimate |
| **Render-dependent** | whether the sheet actually reads well; text sitting on wires; four-way crossing ambiguity; page-edge clipping; annotation covering a route; whether the signal flow is followable; "does it look hand-drawn" |
| **No OA counterpart** | footprint fields (physical binding lives in pcell/layout/techfile); KiCad-style ERC, `PWR_FLAG`, no-connect markers; title block, paper size, off-sheet objects; explicit junction and bus-entry objects |

**Critical adaptation.** In OA a label only *names* a geometric net; it does not
*create* connectivity, which comes from coincident geometry and the global-net
convention. Advice of the form "prefer labels over wires" therefore does not
transfer, and any rule that assumes a label can carry a connection must be
rejected. This Skill's standing position holds instead: an `instTerm` binding
alone is not reviewable, so every terminal needs visible geometry.

## The Render-Review Loop

Repeat per sheet until the target score is met or no fixer applies.

1. **Measure.** Compute the score. If it meets the target, stop.
   Otherwise read `worst_category`.
2. **Plan (dry run).** Select the fixer for `worst_category` and compute the
   prospective change **without writing**. For every candidate, evaluate
   `connectivity_preserved` against this Skill's Save Gate 1 snapshot.
3. **Decide.** If `connectivity_preserved` is false, do **not** apply. Report
   the specific finding and stop that branch. A repair that would change a net
   is not a readability repair.
4. **Apply.** Perform the change inside the already-authorized write set. A
   fixer that would alter connectivity is *refused*, never force-applied.
5. **See.** Render the sheet and inspect the image. Compare against the
   pre-change render. Confirm the difference covers only the objects you meant
   to move. **View the render; do not accept the score alone.**
6. **Re-measure.** Recompute. Confirm the score rose and that no other category
   regressed. Return to step 1.
7. **Guard.** Re-run `schCheck` and re-verify Save Gate 1. A cosmetic pass is
   only acceptable if it also leaves the design warning-free and
   netlist-identical.

### Stopping Rule

Stop when a full pass produces **no applicable change**, even if the score is
still below target. The remaining gap needs human layout judgement, not more
automated nudging. Report what is left and why, rather than grinding the score
by moving objects that should not move.

### The Render Is The Ground Truth

The score is a fast directional proxy. Diagnostics catch what can be
parameterised; they do not catch a crowded layout, poorly aligned text, or a
crossing that is technically legal but confusing. An explicit statement worth
carrying into reviews: a clean diagnostic result is *necessary* but not
*sufficient*, and only an inspection of the rendered drawing settles
readability.

Inspect the render and check, at minimum:

- labels and text do not overlap anything or sit on top of wires;
- spacing is consistent and repeated elements share a pitch;
- wires read as thin lines with small junctions, not as dominant bars;
- no region is so dense that a single net cannot be traced quickly;
- nothing is clipped at the ownership boundary;
- crossings are unambiguous - a genuine crossing never looks like a junction;
- functional islands are visually separable and the flow direction is
  followable;
- the page is split rather than crammed when one sheet cannot stay readable.

### Reference Pair

The upstream Skill ships a matched pair of renders of the *same* three-resistor
circuit: one clean, one with the same electrical content drawn badly (labels
colliding into an unreadable blob, a diagonal wire, off-grid parts at uneven
heights). The pair is useful because it demonstrates the exact defect class
that a clean electrical check cannot see. If a similar before/after pair exists
for this project, use it as the calibration reference instead of an invented
one.

## Reporting

Report the two layers separately, in this order:

1. **Gates** - netlist identity and `schCheck` result, with the evidence that
   actually passed. State explicitly that a clean `schCheck` is necessary but
   not sufficient.
2. **Score** - total, per-category breakdown, `worst_category`.
3. **Render review** - what was actually inspected, what changed between the
   before and after render, and what remains unresolved.
4. **Unverified** - anything checked only by an estimated-text model, anything
   that depended on a render-only judgement, and any finding left open because
   no fixer applied.

Never present a score as proof of electrical correctness, and never present a
clean `schCheck` as proof of readability.
