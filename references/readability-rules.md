# Cross-Tool Readability Rules And Provenance

This is the consolidated rule set behind this Skill. It exists so that every
readability rule has exactly one home, with its evidence grade attached, and so
that rules borrowed from other tools are never presented as if they were
verified for Cadence OA.

Rules already enforced in `SKILL.md` are **not repeated here** - this file
records the numeric calibration, the constraint semantics, and the provenance
that `SKILL.md` deliberately leaves out.

## Evidence Grades

Every rule below carries one of:

| Grade | Meaning |
|---|---|
| `[verified]` | Read line by line in the upstream source during the 2026-10-04 survey |
| `[read]` | Read in upstream prose documentation |
| `[reported]` | Reported by a parallel survey pass; **not** independently verified - re-check before relying on it |
| `[calibrated]` | This Skill's own starting value; **no external validation**, treat as a tunable baseline |

Never upgrade a grade by repetition. If a `[reported]` rule matters for a real
write, verify it first.

## 1. Grid And Coordinate Calibration

| Rule | Value | Grade | Source |
|---|---|---|---|
| Library coordinate quantum | `0.0625` | `[verified]` | this project's confirmed grid; confirmed independently in `virtuoso-cli` (`src/main.rs`) |
| Planning step is an integer multiple of the quantum | `1.5 = 24 x 0.0625` | `[verified]` | `virtuoso-bridge-lite` `schematic/planner.py` default `grid_spacing` |
| Planning step usable bounds | `<1.0` overlaps, `>2.0` wastes space | `[read]` | `virtuoso-bridge-lite` `schematic-recreation.md` |
| Absolute coordinate = lattice index x step | `x = col * spacing` | `[verified]` | `planner.py` coordinate emission |
| Half-grid snapping | `SNAP = 0.03125` | `[verified]` | `cdl_gen/virtuoso.py` - **deliberately not adopted**; this project stays on `0.0625` |
| Off-grid test shape | `abs(v - round(v/g)*g) > tolerance` | `[verified]` | `kicad-mcp-pro` `models/visual_qa.py` `_off_grid` |
| Upstream grid / tolerance (KiCad) | `1.27 mm`, `>0.01 mm` | `[verified]` | same, `detect_grid_misalignment` - reuse the **test shape**, not the number |

The KiCad figures are millimetres for a KiCad sheet. They are recorded to show
the *shape* of a defensible threshold, not to be copied. Re-derive from the
confirmed project grid.

## 2. Placement And Layout Calibration

| Rule | Value | Grade | Source |
|---|---|---|---|
| Row separation by device kind | NMOS/other/PMOS at rows `0.0 / 1.0 / 2.0` | `[verified]` | `planner.py` config defaults |
| Dedicated pin column | `pin_column = -1.0` (left of all devices) | `[verified]` | `planner.py` |
| Output-stage right shift | `output_column = 5.0`, `output_column_step = 1.0` | `[verified]` | `planner.py` |
| Same-cell collision nudge | `new_col += 1.0`, movable keeps fewest hard axes and last name order | `[verified]` | `planner.py` |
| Unconstrained device column order | `float(core_index)` by **name order** | `[verified]` | `planner.py` |
| Partition trigger | `>20` components, multiple signal domains, or `>1` feedback loop | `[reported]` | `vibe-analog` |
| Preferred per-module size | `<=16` components | `[reported]` | `vibe-analog` |

The `1.0`/`1.5`/`2.0`/`5.0` figures are *planning steps*, i.e. multiples of
`0.0625`. They are proposals for spacing, not constraints on where a device may
legally sit.

## 3. Symmetry

| Rule | Value | Grade | Source |
|---|---|---|---|
| Left/right device columns | `center_col -/+ separation/2` | `[verified]` | `planner.py` `DifferentialPairConstraint` |
| Defaults | `center_col = 1.5`, `separation = 1.0` -> cols `1.0` / `2.0` | `[verified]` | same |
| Symmetry axis is **caller-supplied** | never inferred from net names | `[read]` | bridge-lite ADR-0002 non-goals |
| Pair conflict diagnostics | `hard_differential_pair_conflict`, `soft_differential_pair_relaxed` | `[verified]` | `planner.py` |

**Mirroring is decided by transformed pin geometry, not by a mnemonic.** A
survey found two upstream projects using opposite conventions (`left R0 / right
MY` versus `left MY / right R0`) for the same topology. Both are self-consistent
against their own symbol pin placement. The invariant is that the two devices
are **mirror images about the axis**, so that corresponding terminals face the
same trunk. Do not carry a "left is R0" rule across symbol libraries.

## 4. Bounds And Collision

| Rule | Value | Grade | Source |
|---|---|---|---|
| Minimum counted overlap area | `1.0 mm^2` for both text and symbols | `[verified]` | `kicad-mcp-pro` `models/visual_qa.py` |
| Overlap predicate | positive width **and** positive height; edge/corner contact is legal | `[verified]` | same; matches `SKILL.md` geometry gate |
| Estimated text box | `width = len * font * 0.66`, `height = font`; bold `x 1.12` | `[verified]` | same |
| Collision box includes refdes/value text margin | - | `[read]` | `HAbedini-qspice-mcp` `qspice-schematic-layout` |

The estimated-text formula is the only portable way to approximate text extent
without a rasteriser. It is an **estimate**: mark any finding derived from it as
estimated, and never let it alone justify blocking a save.

## 5. Routing And Annotation

| Rule | Value | Grade | Source |
|---|---|---|---|
| Diagonal test | `dx>0.01` and `dy>0.01` and length `>=0.05` | `[verified]` | `models/visual_qa.py` |
| Dense fanout | `>=6` neighbours within `5 mm` | `[verified]` | same - scale the radius to project units |
| Density imbalance | `>=8` symbols, `<=1` occupied quadrant or busiest `>=85%` | `[verified]` | same |
| Font-consistency basis | **mode** of the sizes, ties to the larger | `[verified]` | same |
| Label height default | `0.0625`, with `extension_length = 0.5` | `[verified]` | `virtuoso-bridge-lite` `schematic/ops.py` |
| Dense-value downgrade trigger | `>=8` simple R/L/C **and** `>=4` value strings longer than 8 chars | `[read]` | `404elf/ltspice-codex-skill` |
| Long-wire thresholds | `>20 x grid`; single segment `>360` | `[reported]` | `vibe-analog` |
| Ground symbol count rule | `<=5` shared bus, `>=16` individual symbols | `[read]` | `faisal-shah/agent-skills` `netlist-to-schematic` |

Text that is moved or rotated should be normalised back to horizontal,
left-to-right reading order as a side effect of the move rather than as a
separate repair pass - that is the mechanism `HAbedini-qspice-mcp` exposes via
`normalize_text`, and it prevents a whole class of "straightened the wire, left
the text crooked" defects.

## 6. Constraint Semantics

These are the semantics worth copying even where the implementation cannot be.

| ID | Rule | Grade | Source |
|---|---|---|---|
| X1 | A hard-constraint conflict raises **before any write is sent** | `[verified]` | bridge-lite ADR-0002 and `planner.py` |
| X2 | Hard-constraint error codes are a fixed enumerated set | `[verified]` | `planner.py`: `duplicate_instance`, `duplicate_pin`, `unknown_instance`, `unknown_pair_instance`, `hard_constraint_conflict`, `hard_grid_collision`, `hard_differential_pair_conflict` |
| X3 | Relaxing a soft constraint **must** emit a structured diagnostic | `[read]` | ADR-0002 `ConstraintDiagnostic` |
| X4 | Result is independent of input order; normalise by name and coordinate | `[verified]` | ADR-0002, covered by unit test |
| X5 | Readback comparison tolerance | `1e-6` | `[verified]` | `planner.py` |
| X6 | Readback comparison covers position, orientation, lib, cell, terminal nets, unexpected instances, missing pins, direction | `[verified]` | same |

The transferable idea is a **two-tier constraint model**: invariants abort,
preferences degrade loudly. A planner that silently relaxes a preference
produces a drawing nobody can explain later.

## 7. Connection-Signature Algorithms

Two independent implementations compute a connectivity signature and refuse any
edit that changes it. Both are useful models; they differ in what they can see.

### 7.1 Geometric coincidence (upstream, KiCad)

`[verified]` `kicad-mcp-pro` `tools/schematic_cosmetics.py`:

1. Signature = `frozenset{(set_of_net_names, {(ref, pin)})}`.
2. Point key `(round(x,4), round(y,4))`; union-find; each wire unions its two
   endpoints.
3. T-junctions: a wire endpoint lying in the **interior** of another wire
   (axis-aligned, tolerance `1e-6`, endpoints excluded) unions with it.
4. Labels join their anchor group; power symbols join and their value becomes
   the net name (`PWR_FLAG` excluded); each symbol contributes its pin
   positions.
5. Same-named labels/power names union **across groups** - i.e. connection by
   name.
6. Verdict: before/after frozensets must be **exactly equal**. Coordinates are
   absent from the signature, so translation, rotation about a pin, and
   mirroring are permitted; changing which pins share a net is not.
7. Default dry-run; the signature is recomputed at apply time and the write is
   `refused` on mismatch.

### 7.2 Exported netlist membership (upstream, KiCad)

`[reported]` `schematic-humanizer` `scripts/compare_connectivity.py`, schema
`schematic-connectivity-v1`:

1. `Component(value, footprint, device)` keyed by reference; `Connectivity`
   maps net name -> frozen set of `Pin(ref, pin)`.
2. Reads the exported netlist XML rather than geometry.
3. Validates: empty/duplicate reference, empty/duplicate net name, missing
   node, duplicate node in one net, net referencing an unknown reference, a pin
   in two nets -> error, exit code 2.
4. Compares reference sets, each reference's identity triple, net-name sets,
   and each net's pin set. Case-sensitive, order-insensitive.
5. Ignores net code, coordinates, timestamps, sheet path.
6. Exit codes `0/1/2`, printing the removed and added pins.

### 7.3 What transfers to OA

| Idea | Transferable? |
|---|---|
| Coordinate-free signature (geometry excluded) | **Yes** - strengthens Save Gate 1, letting a pure move be classified as safe without re-deriving the whole contract |
| Union-find over coincident geometry | **Yes**, with OA wire semantics substituted for KiCad's |
| Connection **by net name** across groups | **Yes**, and it is closer to OA's global-net convention than to KiCad's |
| T-junction interior-point union | **Yes** - matches the load-bearing junction behaviour already documented in `SKILL.md` |
| `PWR_FLAG` / ERC concepts | **No** - no OA counterpart |
| Explicit no-connect markers | **No** - OA has no such object |

This Skill's standing position is unchanged and slightly stricter than both:
connection comes from **coincident geometry plus the global-net convention**,
and a label alone never establishes a connection. A signature scheme that
treats labels as connective would be wrong for OA.

## 8. What Deliberately Does Not Transfer

Rules observed upstream but **excluded** here, with reasons:

| Excluded rule | Reason |
|---|---|
| "Prefer labels over wires" as a default | In OA a label only *names* a net; an `instTerm` binding or a label is not reviewable geometry. `SKILL.md` requires visible geometry. |
| Off-sheet symbols, paper size, page-edge clipping | OA has no sheet/paper object; the boundary is the owning island's nearest clear perimeter |
| Title-block completeness scoring | OA has no standard title block. `SKILL.md` substitutes the interface inventory plus the delivery report. |
| Footprint fields | Physical binding lives in the pcell, layout, or techfile, not the schematic |
| ERC / `PWR_FLAG` / no-connect markers | No OA counterpart; `schCheck` plus later LVS is the closest evidence |
| Diagonal wires "legal but discouraged" | In OA, routing through a symbol body or a four-way dotted junction is a **warning-bearing defect**, not a style preference |
| Any rule assuming a label can carry connectivity | Rejected outright for OA |

## 9. Audit Checklist

Adapted from the upstream visual-audit checklist `[reported]`. Items marked
**OA** were re-scoped because the upstream item assumed a KiCad sheet.

**Wiring**

- Do not treat a higher wire count as an improvement.
- A bus trunk must not cross a symbol body, value, reference, note, or
  unrelated label.
- Two different buses must not be collinear or overlapping.
- Avoid wire-through-pin ambiguity; branches and junctions must be explicit.
- Use the native grid and snap entries; keep entry pitch and direction
  consistent. **(OA)** There is no bus-entry object; the equivalent requirement
  is uniform stub length and pitch at a pin bank.
- Each polyline vertex is its own segment; split a trunk at a T-junction.
- Pull-ups, terminations, decoupling, and interface passives sit near the
  circuit they serve.

**Whole sheet** **(OA re-scoped)**

- Main signal flow reads left to right, or in the project's confirmed order.
- Functional grouping matches the title or the owning island's note.
- No connector, support circuit, or power chain appears to float.
- No long loops, label flooding, clipped text, or large blank gaps that hide a
  broken path.
- Every owner boundary and every cross-boundary endpoint is accounted for.

**High-density crops**

- Large ICs, modules, and memories.
- High-speed, RF, clock, and external connectors.
- Pin banks with many parallel stubs.
- Power OR-ing, regulation, reset/start-up, and glue logic.
- Any region changed since the previous render.

**Annotation gate**

- No annotation covers a wire, bus, pin, reference, value, or functional title.
- A URL is never clipped.
- No annotation interrupts the visual signal path.
- Density never degrades scannability; detail tables move to the companion
  report.

**Acceptance** - all must hold

- Every sheet passes at full-page render.
- Relevant interfaces and changed regions pass at crop render.
- No visible overlap, no ambiguous junction, no apparently floating local
  function.
- The connectivity comparison and `schCheck`/lint pass **independently**.
- The completion report displays or links the final snapshot.

An explicit point worth keeping: **passing an electrical check does not pass the
visual audit**, and passing the visual audit does not prove electrical
correctness.
