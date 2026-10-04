---
name: cadence-schematic-generation-readability
description: Plan, generate, reorganize, and review schematics for compact functional placement and readable explicit connectivity without changing terminal-to-net semantics. Use for Cadence OA schematic automation when placement, functional frames and annotations, labels, stubs, repeated branches, or symbol orientation could hide connectivity errors, and for bridge-driven creation, where the bridge's schematic Python API and reference tree come before hand-written SKILL; route electrical or supported connectivity-display snapshots to cadence-oa-snapshot-read. Also use when a schematic is redrawn as a standalone figure - SVG, PDF, PNG, EMF, or HTML canvas - from a user reference sketch or an embedded Visio/EMF source, even with no Cadence session, because the figure's own net declarations carry the same terminal-to-net contract. Also use when a schematic passes every electrical check but still reads poorly, because this skill carries a deterministic 0-100 readability score with a score-render-rescore review loop, and is the single home for schematic readability with cross-tool adapters for KiCad, LTspice, QSpice, xschem, and standalone figures while Cadence OA remains the authoritative adapter. Full schematic drawing geometry requires a separately supported read path. This skill does not establish circuit function, simulation correctness, or signoff.
metadata:
  skill_type: "cadence-automation"
  skill_type_zh: "Cadence 自动化"
  skill_tags:
    - "skill-type/cadence-automation"
---

# Cadence Schematic Generation Readability

Produce a schematic whose visible structure explains the circuit while its electrical structure remains exactly traceable to authoritative connectivity.

## Reference Map

This Skill is the single home for schematic readability. Read the entry sections
below for the workflow and the gates; open a reference only when its topic is in
scope for the current task.

| Reference | Read it when |
|---|---|
| [readability-rules.md](references/readability-rules.md) | You need the cross-tool rule set with evidence grades, numeric calibration, constraint semantics, connection-signature algorithms, or the audit checklist. Also the place to check before quoting any borrowed threshold |
| [readability-scoring.md](references/readability-scoring.md) | The task asks whether a schematic is readable, clean, or professional; or you are about to run a beautification or cosmetic repair pass |
| [layout-algorithms.md](references/layout-algorithms.md) | Placement is genuinely under-determined and must be computed rather than chosen: layering, crossing minimisation, obstacle-avoiding routing, constraint-weighted search |
| [tool-adapters.md](references/tool-adapters.md) | The work is **not** Cadence OA - KiCad, LTspice, QSpice, xschem/XCircuit, a SPICE-to-Circuitikz figure, or a standalone SVG/PDF/EMF drawing |
| [compact-functional-block-style.md](references/compact-functional-block-style.md) | A user marked an existing region as the correct style, or a generated analog block is electrically connected but visually scattered |
| [hierarchical-mixed-signal-readability.md](references/hierarchical-mixed-signal-readability.md) | Composing a hierarchical TOP, placing pin banks, or handling mixed-signal interfaces |
| [review-checklist.md](references/review-checklist.md) | Running a pre-generation or post-generation review |

**Precedence.** The entry sections of this file and the two Save Acceptance
Gates outrank every reference. If a reference appears to permit something the
gates forbid, the gates win and the reference is wrong - report it rather than
acting on it. Cadence OA is the authoritative adapter; the other tools in
`tool-adapters.md` are narrower and their constants never transfer to OA.

## Use The Bridge Schematic API First

For bridge-driven work, first read the installed bridge's own API inventory and
the relevant upstream signatures/examples. Reuse a helper when its geometry,
write scope and save behaviour satisfy this task. If they do not, reuse its
suitable builders or use documented SKILL for the specific gap; upstream origin
alone does not establish suitability.

| Intent | Required choice |
|---|---|
| Create a new view | Verify that the exact target does not exist before choosing mode `"w"`. |
| Modify an existing view | Use append mode `"a"`; preserve protected objects. `modify()` selects this mode, but still auto-saves on normal context exit. |
| Rebuild an existing view | `create()` selects mode `"w"` and replaces the view. Use only with explicit replacement scope compatible with protected pins; deleting the whole cell is not an alternative. |

The current `SchematicEditor.__enter__` queues the open operation; normal
`__exit__` submits edits, `schCheck`, and `dbSave` in one batch.
It neither conditions saving on zero warnings/errors nor rolls back earlier
mutations. Do not use that default auto-save context for this Skill's
save-gated workflow. Both `create()` and `modify()` have this limitation.

Prefer the existing operation builders for the planned mutation. This
planning-only example generates a command string; it opens no view and
executes no SKILL. Arguments come from the confirmed master and placement plan:

```python
from virtuoso_bridge.virtuoso.schematic import schematic_create_inst_by_master_name

instance_command = schematic_create_inst_by_master_name(
    master_lib, master_cell, "symbol", instance_name, x, y, orientation
)
```

Execute the authorized write using the existing stages below: bind and
preflight the exact view; apply the bounded batch without an implicit save;
inspect the in-memory electrical and geometry result and obtain the actual
`schCheck` diagnostics; save only when **Save Acceptance Gates** and
**Enforce The Pre-Write Pin And Geometry Gate** both pass. A failed or unknown
check stops before `dbSave`; reconcile partial state before any retry.
An operation builder plus a single batch is not an atomic OA transaction.

Helper limits matter:

- Terminal lookup takes the first pin/figure; resolve multiple access points explicitly.
- MOS escape directions use master-name and terminal-name heuristics. Accept them only when consistent with transformed master geometry and the selected access point.
- `cosmetic="clean"` and `auto_rotation=True` are placement heuristics, not overlap or clearance checks.
- Builders take explicit coordinates/orientations; they neither require repositioning existing instances nor guarantee grid alignment. Preserve authorized coordinates and run the existing grid/contact checks.
- Label stubs do not replace required explicit local wiring. See the inventory's conflicting historical glue observations before selecting `bind_label_to_wire`.

## Scope And Evidence

- Apply the workflow across processes, device libraries, and circuit topologies. Discover the current host, process, PDK, profile, library, cell, view, master symbols, terminal names, grid, and dimensions at run time; never encode them as universal defaults.
- An audit or planning request is read-only. Before any live Cadence, CIW, OA, or bridge write, obtain explicit authorization for the exact target and write set, confirm the current profile, and pass that profile explicitly on every bridge command.
- Authorize each OA view independently. Permission to edit a `schematic`, clean an interface, update parent wiring, or make hierarchy views consistent does not authorize a `symbol` write. Before creating, rebuilding, or changing a symbol, obtain current-task confirmation for the exact `library/cell/symbol` target and the concrete terminal, direction, bank/order, body, title/text, and known parent-impact changes. Without that confirmation, report any schematic/symbol mismatch read-only and stop before opening the symbol appendable.
- Treat every existing schematic or symbol boundary terminal and pin as a protected object by default, especially user-created supply and ground pins. Authorization to add functional logic, clear placeholder contents, rebuild internal circuitry, or replace instances does not authorize deleting, moving, recreating, renaming, or changing the master of a boundary pin. Migrating a pin requires separate current-task authorization for the exact view, named pin, operation, and target coordinate or placement rule.
- Repacking, compacting, framing, pin-bank optimization, and whitespace cleanup below apply only to new objects or objects explicitly authorized for the respective move or edit. Report legacy spacing or whitespace caused by protected objects; never expand the write set to remove it.
- A fresh netlist and current OA instance-terminal-to-net mappings are the electrical authority. Screenshots and visual appearance can expose readability defects, but they cannot prove connectivity or terminal identity.
- Prefer direct netlist text, structured OA queries, and logs over GUI inspection. Do not use Computer Use to select a symbol and press Space to discover or change orientation.
- Separate evidence classes: intended topology, current OA connectivity, visible drawing geometry, cross-view consistency, generated-netlist connectivity, and functional verification. A pass in one class does not imply a pass in another.
- Route current electrical or supported connectivity-display evidence to `cadence-oa-snapshot-read`. That Skill does not provide full schematic instance placement, wires, junctions, or arbitrary drawing geometry. For those reads, verify an existing getter-only schematic geometry path or report the capability gap; this does not authorize a new exporter, OA writes, or GUI input. Do not add backup, hashing, screenshots, persistence checks, or a before/after evidence package until the user authorizes a write or explicitly requests an audit artifact.

## Project Grid Overrides

An explicitly confirmed project grid takes priority over generic pin-bank pitches in this file and its linked guides/checklists. For `the project workspace`, the user's current correction (2026-09-18) is a schematic grid of `0.0625` units; it supersedes the 2026-09-06 note that recorded `0.625`. New geometry and separately authorized moves must lie on that lattice relative to the verified view origin; new bank pitches must be whole grid steps with sufficient visual clearance, not `0.125`. Check that the actual view grid can represent the planned lattice; report an incompatibility rather than changing view settings or moving protected legacy pins. This does not authorize any symbol-view or parent-interface change.

Keep the local bridge's six-decimal coordinate serialization independently of this placement rule. Formatting with `.6f` neither proves grid alignment nor authorizes quantizing arbitrary geometry or other projects to this grid.

## Establish The Connectivity Contract

Before placement, record a machine-readable or tabular connection plan with at least:

`instance | master | master terminal | intended net | functional block | allowed change`

For an existing design, derive this table from a current netlist and current OA mappings, including each instance terminal's actual net. For a new design, derive it from user-confirmed circuit requirements and approved master terminal definitions, then use the generated OA and netlist to verify it. Do not infer terminal identity from how a symbol happens to look.

At every hierarchical boundary, key the contract by exact terminal name and electrical role across the child schematic terminal, child symbol pin, parent instance terminal, and parent real net. Never pair or reconnect interfaces by array index, enumeration order, or pin coordinates.

Treat terminal-to-net assignments as invariant during readability-only work. Never exchange drain, source, gate, bulk, polarity pins, switch terminals, or any other terminals to make placement or routing easier. A topology-specific PMOS or NMOS drawing convention is an example, not a universal orientation rule.

Before any clear or rebuild helper can run, freeze an exact boundary-pin manifest containing terminal object identity, name, case, direction, `sigType`, net identity and name, pin master, every pin figure and its `xy`/orientation/BBox, owned terminal-name displays, owned electrical stubs/rails/labels, and the current view snap/grid and origin. Existing pin coordinates and owned geometry remain authoritative unless that exact pin passed the separate migration gate. New internal logic must bind by exact name to the retained boundary net; it must not recreate or move a boundary pin for generator convenience.

Freeze every required producer-to-consumer relation as an endpoint-cardinality contract, not merely a port inventory. Expand instance arrays into their actual elements, then every bus terminal into scalar bits. State explicitly whether a scalar net broadcasts to all elements or a vector maps bitwise, preserving declared index order; a device `m` parameter is not automatically an instance array. Use the same scalarization for the pre-save endpoint checks and fresh-netlist comparison. Record, for each required input bit, its one legal driver, and for each required output bit, its exact consumer set. Reject automatic parent-net substitutions, a required input with zero or multiple legal drivers, a required output with a missing or unexpected consumer, and multiple required outputs driving one net. A deliberately unconnected input, unused output, or no-connect endpoint must be named and justified in the contract; never infer a waiver from an automatic net name, endpoint count, or familiar signal name. Port counts, order, set equality, and `schCheck` do not establish this endpoint relation.

### Net-Name Uniqueness And Disambiguation

A net list must be unambiguous by inspection. Within one cellview - and within one generated or edited subcircuit - never create two distinct nets whose names differ only by a separator, letter case, or leading zeros, for example `net06` against `net_06`, `net11` against `net_11`, or `net16` against `net_16`. Such a pair is a defect even when both names are individually legal to the tool, because a reader, a reviewer, and a later script cannot tell them apart reliably.

Normalize before generating or renaming: strip `_` and `-`, fold case, and drop leading zeros from a purely numeric tail. Two different names that share one normalized form are a blocking conflict. Run the check over the names you are about to create together with every name already present in the view, and stop rather than inventing a disambiguating suffix by taste.

Legacy pairs are read-only facts, not a licence to rename. Renaming an existing net changes the netlist and therefore violates the readability gate, so a historical pair such as `net16`/`net_16` stays exactly as it is. Instead: (a) publish a mapping table in the deliverable or connection contract stating what each member of the pair actually is, and (b) forbid new names of the same shape anywhere in that cellview - schematic, symbol, layout, Maestro variables, and the accompanying documents. When new logic must be added next to a legacy pair, derive its node names from function (for example `N_TC_OUT`) rather than from a counter that recreates the ambiguity.

The same rule governs documentation: a report may quote a legacy pair only together with the mapping table, and must not introduce its own look-alike labels.

## Save Acceptance Gates

Two user-confirmed gates (2026-09-18) apply to every schematic write, generated or edited. They are acceptance conditions, not optional checks, and both must pass before `dbSave`.

1. **A readability change must not change the netlist.** For any drawing-only, beautifying, repacking, framing, labelling, or junction change, take a same-cell electrical snapshot immediately before and after the edit and require an exact match: every `instance/terminal -> net` tuple, the net count, and the boundary port set with names and directions. Compare drawing data separately; a zero electrical diff with a nonzero geometry diff is a drawing-only change. When a fresh netlist for that cell exists, additionally diff its subcircuit section against the pre-change one instead of relying on the OA snapshot alone. If the readability goal cannot be reached without moving a terminal to another net, splitting a net, or creating a new one, stop and report the conflict; never save such a change as "readability".
2. **A schematic may be saved only when it is warning-free.** Run `schCheck` against the exact state that will be written and require zero errors and zero warnings before `dbSave`; on anything else, stop and report rather than saving first and disclosing afterwards. Floating, dangling, or unused wire and label objects, and schematic-versus-symbol terminal-direction mismatches, are defects to fix rather than acceptable noise. Deleting an unused wire stub is safe only when the net name is still produced by a retained label or by the confirmed contract; re-verify the net names and the net count afterwards. Resolve a terminal-direction mismatch by making the side that disagrees with the confirmed interface contract match it, and state which side changed and why.

A clean `schCheck` is necessary but not sufficient: it does not prove netlist identity, geometry non-overlap, or circuit function. Report the two gates separately with the evidence that actually passed.

### Legacy Wide Wires Are Load-Bearing

A finished cell may carry two-point `wide` wires (`objType "path"`, `~>width 0.0125`) that both join a pin to its net and **own the wire label that names that net**. An audited cell held 72 of them across its supply, internal-rail, and mirror-control nets, and a first naive pass split it from 50 nets into 108 with 137 `floating input/output` warnings.

The failure is a **lost net name, not a lost connection**. Deleting a `path` also deletes the wire labels it owns, and the label re-creation then failed silently because `schCreateWire` returns `l_wireId`, a **list** of wire ids: handing that list to `schCreateWireLabel` as `d_glue` raises `SCH-1001 Invalid value specified for argument "glue"`. The earlier reading - that the copper overlap itself was load-bearing and the bars could not be thinned - was wrong; it followed from that hidden label-creation failure. A single-bar probe confirms the mechanism: with a real wire id the thin replacement kept every `instance/terminal -> net` tuple unchanged, and only the label disappeared.

Verified thin-wire conversion (2026-09-18, `LIB/CELL/schematic`, all 36 remaining bars, both gates passed before `dbSave`):

1. Snapshot the whole electrical contract first: every `instance/terminal -> net` tuple, the cell terminal set with names and directions, the net count, and the **complete label inventory** (text, height, orientation, justification, position).
2. Per bar: collect the labels whose bounding-box centre falls inside the bar, delete the bar, create `schCreateWire(cv "draw" "" points 0.0625 0.0625 0)`, and glue each collected label back with a real wire id, `glue = car(car(errset(schCreateWire(...))))`. `schCreateWireLabel(cv glue point text justify orient fontStyle fontHeight nil)` requires all nine arguments.
3. Repair pass: every label of the saved inventory that is still missing (its centre lay outside its own bar, as with end-justified labels) is glued to a wire running through the old label position - exact containment first, then one-grid (`0.0625`) tolerance. In the audited cell the per-bar pass restored 23 labels and the repair pass the remaining 6.
4. Gate before saving: zero electrical diff against the frozen snapshot, `schCheck` 0 errors / 0 warnings, and a centre-line check that every old bar's point list exists as a thin `line` at identical coordinates (36/36 in the audited cell). Keep the pre-change `sch.oa` copy for rollback.
5. No per-bar confirmation is needed once the view is inside the authorized write set: the standing rule is that the finished drawing contains no `type=wide` wire, so legacy bars are converted as part of the pass that is already authorized. Report the bar-by-bar electrical diff, not an offer to convert them later.

SKILL-engine pitfalls seen here: `schCreateWire` returns a list, not a single figure id; `( if(...) )` is a call on the result of `if`, not a grouping, so an `if` passed as an argument must not be wrapped in extra parentheses; `(- a b)` is not a function (use `difference(a b)`); and a `prog` local list must name every variable the body assigns.

The verified converter is kept as [scripts/thin_wide_wires.il](scripts/thin_wide_wires.il): call `TW_OPEN(lib cell)`, freeze `TW_PRE = TW_SNAP()`, run `TW_RUN()` (which already contains the repair pass), evaluate both gates against `TW_PRE`, and only then `TW_SAVE()` or `TW_ABORT()`. It loaded and smoke-ran cleanly on the already-thinned cell (`bars=0`), but it has not yet been exercised on a second cell that still carries wide bars.

### Cross-Over Junction Warnings

`schCheck` reports `Solder dot on cross over` at a point where more than two wire branches meet with a solder dot, typically a four-branch `+` junction carrying an automatic dot. Such a dot is load-bearing: deleting it converts the junction into a two-wire overpass and disconnects the nets, and replacing the four collinear segments by continuous through wires keeps the warning while splitting the net. Either outcome violates gate 1.

The accepted repair is a drawing-only change that splits the four-branch point into two three-way T junctions: keep every far endpoint and the real connection, and re-attach one branch through a short on-grid step so that no point carries four branches. Verify with both gates. A step of four `0.0625` grid units was sufficient in practice: the cell then saved with zero errors and zero warnings while every `instance/terminal -> net` tuple remained identical.

## Score And Render-Review

The gates above are binary and prove an unchanged, warning-free drawing. They do
not distinguish a well-drawn schematic from a badly drawn one: a sheet can pass
every gate and still be unreadable. For requests that ask whether a schematic is
readable, clean, professional, or reviewable - and for any beautification,
repacking, or cosmetic repair pass - apply
[the readability scoring and render-review guide](references/readability-scoring.md).

Two rules from that guide govern this Skill's own workflow:

1. **Gates outrank scores.** The score is advisory and never excuses a failed
   gate. Report the gate layer and the score layer separately; never merge them
   into a single verdict.
2. **The render is the ground truth.** A clean diagnostic result is necessary
   but not sufficient; only inspection of the rendered drawing settles
   readability. Do not accept a score, or a clean `schCheck`, as a readability
   conclusion.

The scoring guide's penalty table mixes weights carried over from a verified
upstream implementation with weights calibrated for this Skill. Do not quote a
calibrated weight as an established fact, and re-derive the grid and overlap
thresholds from the confirmed project grid instead of copying the upstream unit
values. The guide's stopping rule also applies here: stop when a full pass
produces no applicable change, even if the score is still below target.

## Figure-Level Redraw Outside OA

This Skill also governs a schematic delivered as a standalone drawing - SVG, PDF, PNG, EMF, or an HTML canvas - redrawn from a user reference sketch, an embedded Visio/EMF source, or an existing figure, even when no Cadence, CIW, bridge, OA, or netlist-generation path is involved. A figure's connectivity lives in its own declarations (a `net(...)`-style netlist, pin bindings, or route endpoints); every terminal-to-net rule above applies to that contract unchanged, and a visually convincing render is not evidence that the contract survived.

- Declare the authority split before the first edit and hold it for the whole task. A **reference sketch** governs intended topology, block boundaries, reading order, and which relations stay explicit; an **extracted netlist** governs device identity, sizes, terminal names, and per-device connectivity. When the two appear to disagree, report the exact difference and ask which one is authoritative. Never resolve it by taste, and never treat a netlist-level fact as authority over how the figure should be drawn.
- A drawing-only request - lead length, equal leads, label or annotation placement, compactness, junction dots, deleting an annotation, a wire that runs through a symbol body - authorizes geometry and text only. It never authorizes adding, splitting, merging, re-scoping, or deleting a net declaration or a device terminal, and it never authorizes renaming a device. Report such a finding as a separate proposal, with the evidence and the exact proposed edit, and wait for the decision before touching connectivity.
- Extract the vector source before judging any connectivity. A `pptx`, `docx`, or `pdf` frequently embeds a `vsdx` package or an EMF/SVG preview that yields exact segment endpoints; parse it and record those coordinates as the evidence. Thumbnails, screenshots, and downscaled images are not connectivity evidence, and re-examining them is not progress.
- Derive every port and device coordinate from resolved pin geometry instead of a hand-written number. One grid step of error silently introduces a jog, and a route waypoint that merely passes through a pin coordinate is not a connection.
- Require both conditions before calling a pin connected: it is enrolled in the intended net's terminal set, and at least one routed branch actually ends on it, either as a terminal endpoint or as a junction lying exactly on that pin. A polyline that crosses a pin without ending there is a defect.
- Machine-check the figure before delivering it: every drawn pin enrolled in exactly one intended net, every net's enrolled pins reachable through one connected component of that net's own branches, and every branch landing on its declared endpoint. Overlap and spacing checkers cannot detect a split or merged net, so a clean render is never electrical evidence.

## Plan Placement Before Writing

1. Partition the circuit by function, signal flow, and power domain. Keep inputs, processing stages, feedback, bias, protection, switching, and outputs in a coherent reading order appropriate to the actual circuit.
2. Keep devices that express one local relationship close together. Current mirrors, differential pairs, cascoded stacks, protection networks, switches, and bias branches should show their shared local nets with explicit nearby wiring rather than scattered duplicate net names.
3. Use short continuous wires inside a functional block. Reserve net names primarily for cross-block or truly global connections, including power and other intentionally shared domains.
4. Align repeated branches with consistent orientation, spacing, and role order. Make power rails visually clear. Keep the drawing compact, but never reduce its extent by overlapping symbols, text, pins, labels, or unrelated wires.
5. Before assigning coordinates, compute each object's full visual bounds: symbol body, pin access and figures, pin names, instance name and properties, power pins, and existing or planned connection stubs. Use the union of those bounds plus explicit clearance for placement; a body-only BBox is insufficient.
6. Use the confirmed project grid where specified, together with the active view grid, origin, and dimensions as described in Project Grid Overrides; otherwise use the discovered view grid. Numerically snap and assert every coordinate of a new instance, line, label, junction, and any separately authorized pin move before mutation; a hard-coded value that happens to look like `0.0625` or `0.125` is not grid evidence. Re-run contact analysis on the snapped plan and stop if snapping creates a touch, merge, or topology change. Preserve a protected legacy pin exactly even if it is off-grid, report that baseline condition, and do not silently "fix" it. Where compatible with the confirmed grid, the `0.125` schematic-unit pitch applies only to compact same-direction external signal-pin banks; never reuse it as top power-group, internal standard-cell, level-shifter, or hierarchical-module spacing.
7. When an authorized cleanup removes obsolete terminals, disabled or `nlAction=ignore` instances, or an inactive functional island, recompute placement, pin-bank membership, frames, and visible bounds from the surviving active content. Do not retain deleted indices as blank bank slots, preserve an empty legacy frame, or leave a large hole merely because the old coordinates existed.

## Enforce Visual Geometry And Native Wire Semantics

- At TOP level, do not mechanically stack hierarchical instances at a fixed increment. Arrange them by signal flow and full visual bounds so symbol bodies, pin banks, pin names, instance names, supply pins, and stubs never intrude into one another. Inside standard-cell or level-shifter schematics, align cells within one functional domain and leave larger clearance between different domains.
- Treat symbol-to-symbol non-overlap as a hard invariant for every placed schematic instance. Transform all four corners of each authoritative symbol-master BBox through the instance's complete transform/orientation, normalize the resulting axis-aligned BBox in parent-view database units, and compare every unordered instance pair. An intersection is a blocking overlap exactly when it has positive width and positive height; edge-only or corner-only contact is not overlap. If a master BBox or transform cannot be established unambiguously, stop rather than infer it. Report each failure with both instance names, both `library/cell/view` master identities, both transformed BBoxes, and the intersection BBox.
- Do not waive or conceal a symbol overlap through layer choice, color, draw order, zoom, hidden text, or a clean `schCheck`. Fix it only by moving an instance that is new in the authorized transaction or explicitly authorized for rearrangement; never move an existing user instance, boundary pin, supply/ground pin, or unrelated circuitry merely to clear the gate. A design that intentionally requires overlapping instances needs a newly confirmed requirement change before generation or save.
- Discover the approved schematic's existing wire LPP, ordinary wire width, bus convention, and label style before generating geometry. Every scalar net uses the same ordinary thin wire style; only a genuinely multi-bit bus may use bus or thick-line semantics. Independent one-hot nets such as `STATE0` through `STATE7` remain eight scalar wires. Do not put a physically wide `dbCreatePath` on every terminal as a generic connection method.
- **Connection wires are narrow `line` type only** (user rule, 2026-09-18). Create every generated or repaired net wire as a width-0 line - `schCreateWire(cv "draw" "" points spacingX spacingY 0)` - and never as a width-carrying wire, a `dbCreatePath`, or a thick/tap-style bar used to bridge a gap between two pins. A wire that the schematic editor reports as `type=wide`, or any net wire whose `~>width` is non-zero, is a defect in geometry you produced.
- Give every supply, ground, body, well, and intermediate-rail terminal a clear visible rail or short stub bound to its real OA net. If an ordinary stub pass filters power nets, a separate supply generator must cover every excluded terminal; hidden binding or supply text alone is not acceptable.
- Plan each pin escape from the transformed full pin figures, electrical access point, wire width, required clearance, and current grid. Adjacent pins on different nets, especially supply and ground, require one-to-one exclusive escape lanes; applying the same generic escape vector to both is illegal unless the resulting clearance envelopes are proven disjoint.
- Before creating ordinary electrical lines, compute pairwise contact for every planned pin figure and segment. Distinct intended nets must have no shared endpoint, endpoint-on-segment contact, T-intersection, collinear overlap, foreign-pin intrusion, junction, zero-clearance/line-width contact, or other clearance-envelope overlap. Attaching each figure to a different net with `dbAddFigToNet` does not make touching geometry safe. A different-net visual crossing is allowed only through an explicit project-native nonconnecting crossing or gap whose no-junction, no-shared-endpoint, no-endpoint-on-segment, no-pin-intrusion semantics are confirmed by the native checker; ordinary crossing lines are not an inferred exception.
- Give every electrical junction an explicit owner. All incident pin figures and segments must resolve to one OA net identity, name, `sigType`, and power domain. After the complete snapped plan and again after in-memory creation, build conductive geometry connected components using the project-native wire, pin, junction, and crossing semantics; each component's net identity/name/`sigType`/domain sets must each have cardinality one.
- Only after the symbol-specific authorization gate passes, create or revise a symbol from a user-approved symbol in the same project as the geometric and stylistic exemplar. A confirmed cell such as `EXAMPLE_SYMBOL` is an exemplar case, not a cross-process required cell or master. Copy its visual relationships and object roles, not its absolute coordinates or dimensions. Size the body to contain its pin banks, required title, and text without meaningless empty area; group left and right pins by function and keep producer output order consistent with consumer input order. Do not delete or hide the identifying title merely to shrink the body unless the user explicitly approves a titleless exemplar. Inputs-left, outputs-right, supplies-top, and grounds-bottom remain project conventions unless an approved exemplar-derived template below makes a narrower rule explicit.
- Treat analog readability as a hard acceptance condition. Never clear a readable analog drawing and replace every MOS terminal with isolated mechanical stubs. Preserve a user-approved old geometry or backup as a protected exemplar during interface migration or digital-cell removal, including MOS placement, current-mirror T-routes, and local relationships.
- A segmented mixed-signal driver containing the corresponding roles must expose distinct `strong VCM`, `weak VCM`, `P fast`, `P slow mirror`, `P three-level protection`, `N fast`, `N slow mirror`, and `N three-level protection` islands. Apply the detailed analog-island and traceability rules in [the compact functional-block style guide](references/compact-functional-block-style.md).
- For hierarchical TOP composition, name-keyed interfaces, supply coverage, pin banks, approved symbol geometry, producer-versus-consumer port roles, compact `LEVEL_SHIFTER` and digital-cell wiring, transmission gates, protected analog exemplars, and scoped rollback, apply [the hierarchical mixed-signal readability guide](references/hierarchical-mixed-signal-readability.md). Its exemplar-derived templates are hard gates when that visual grammar is selected; they do not make the named exemplar cell a cross-process dependency.
- Before generating, repairing, or retrying an OA drawing transaction after a prior script failure, re-read `## Execute One Controlled Write` and `## Close Recovery By Exact View Set` above and honour every stop gate in them. A retry after an unknown partial state is never automatic.

## Frame And Annotate Functional Blocks

- After a functional block has been placed and routed, optionally enclose it with one visible non-electrical rectangular frame when the grouping materially improves review. Derive the frame from the final union of device, wire, junction, instance-name, parameter, pin-text, and local-label bounds, then add consistent minimal padding on the active grid.
- Put one short functional annotation at a consistent outside edge of the frame, normally below or above it where local clearance is greatest. The note should name the block or its engineering role, such as a reset-to-common-mode path or a fast-bypass/slow-mirror driver; it must not cover wiring or become a substitute for readable topology.
- Create the frame and note on the project's existing non-electrical drawing/annotation LPP. They must have no net, terminal, pin, or connectivity meaning. A white frame and colored note are display-resource effects in one environment, not portable layer or color requirements.
- Keep one frame per meaningful functional island. Avoid nested, overlapping, oversized, or device-by-device boxes. A frame must not cross symbols, wires, labels, or another block's boundary, and adjacent frames need enough separation that their ownership is unambiguous.
- The circuit inside the frame must remain compact without becoming crowded. Minimize empty area and avoid long detours, but preserve visible clearance among symbols, instance names, parameter text, pin names, net labels, junctions, and routes. Move or reroute the electrical objects first; never enlarge a frame merely to excuse a scattered block or shrink it until text and wires collide.

## Place External Interfaces At The Cell Boundary

- Only after an explicit interface-layout authorization, enumerate every schematic terminal and assign each pin to a named boundary bank or an explicit, justified exception. An internal-logic generation request leaves the existing boundary manifest protected. If the user asks to optimize "the IOs" or "all pins" without naming a subset, the authorized layout target is the complete schematic pin inventory; do not move only the most conspicuous pins and report the interface as complete.
- Plan external interface banks together with the functional blocks. Do not leave a pin at the historical coordinate of a device or branch after that function moves elsewhere; an interface pin belongs to the current cell boundary and signal-flow plan.
- In a schematic view, treat that boundary as the nearest clear perimeter of the active functional composition or the pin's owning island, not a page-scale rectangular edge chosen from the farthest object. Place control, bias, common-mode, and output handoff pins where short real-net stubs make ownership obvious. Symbol-view pins remain a separate contract and must land on the actual symbol-body border after symbol-specific authorization.
- Choose the boundary side from the actual interface role, user-approved exemplar, and signal flow. Inputs may form a left bank, outputs or analog handoff pins a right bank, and supplies a top or bottom bank, but none of those sides is a universal rule.
- Align signal pins in a compact on-grid row or column. Subject to Project Grid Overrides, the default center-to-center pitch for a same-direction signal-pin group is `0.125` schematic units, independent of process and PDK. Put each electrical access-point center exactly on the symbol-body boundary, its pin figure outside, and its horizontal visible pin name inside; never inset the body border away from left, right, or top access points. The pin figure, name, symbol border, and neighboring symbols must have nonzero visual clearance. Avoid isolated pins floating across otherwise empty canvas. Power and ground groups may instead use the approved exemplar's compact top-group spacing, but must never be averaged across the full body width.
- Decide first whether signal pins are separate functional-band interfaces or members of one signal bank. Once signal pins are assigned to one bank, the grid-compatible confirmed pitch (`0.125` only where no project override applies) and one shared boundary coordinate take priority over matching each pin to the vertical or horizontal position of its internal circuit block. Preserve functional association through deliberate order, names, and explicit gaps between groups, not by stretching one bank across the page. If text collides, first adjust its horizontal position, the bank order, symbol width, or a group gap; do not rotate or hide signal terminal names or silently enlarge the signal group's pitch. Report a genuine unresolved conflict before deviating from the confirmed pitch. Do not add long wires merely to reach a boundary pin when the terminal and the internal branch already share the same named OA net.
- A readability-only pin move changes the schematic pin figure and its owned display geometry, not the terminal contract. Preserve terminal name, case, direction, net, pin identity, and hierarchy consumers; do not recreate the terminal or alter the symbol/parent interface unless that larger scope is explicitly authorized.
- Move the pin figure and terminal text as one visual unit. Keep signal terminal names horizontal, visible, and on the interior side, with clearance from devices, parameters, neighboring pins, and wires. A top power-pin name may retain the approved exemplar's established direction when that exact style is selected. Derive the pin figure orientation from the actual pin master and transformed access point rather than guessing from the pin type.
- Completion requires an inventory result for every terminal: final bank, coordinate, orientation, adjacent pitch, and preserved electrical contract. A compact bank on one side does not compensate for scattered banks on the other sides.

## Preserve Approved Exemplars And Their Visual Grammar

When the user identifies an existing region as a correct example, first translate that approval into an explicit protected set: instances, origins and orientations, terminal-to-net mappings, local wires, junctions, labels, and any other drawing objects the user included. Treat that set as read-only during adjacent cleanup unless the user later authorizes a specific change. Do not redraw a correct exemplar merely to make the whole page mechanically uniform.

Extract only portable visual rules from the exemplar. A compact analog block typically reads well when it forms one bounded functional island, uses a short shared trunk for a genuinely shared local net, aligns devices by circuit role, places directly related devices on neighboring grid locations, and uses explicit orthogonal wiring to expose branch and stack relationships. Local topology should remain understandable without reconstructing a chain of repeated net labels.

Do not universalize incidental details such as a particular PMOS direction, device order, rail location, canvas coordinate, or process-specific symbol shape. Re-derive those choices from the current circuit, transformed symbol pins, active grid, power domains, and user-confirmed signal flow. The cross-process schematic signal-pin-bank default is `0.125` schematic units only where compatible with Project Grid Overrides. Apply [the compact functional-block style guide](references/compact-functional-block-style.md) when reproducing an approved drawing style or reviewing an overly scattered analog block.

Approval of a local transmission-gate repair does not authorize clearing or rearranging the surrounding analog schematic. User-approved current mirrors, fast and slow branches, and their local routes remain protected exemplars. If a failed attempt affected them, first follow [Close Recovery By Exact View Set](#close-recovery-by-exact-view-set); choosing a narrow region does not waive current recovery authorization, provenance, or user-drift checks. Only after that contract is satisfied, restore the narrowest authoritative affected region or view, re-establish its electrical and geometry baselines separately, and then patch only the explicitly authorized transmission gate.

Treat ignored or disabled instances as visible schematic content, not as electrically removed whitespace. If they remain for a documented reason, include them in extent and clutter review. If an interface audit and the exact write authorization classify them as obsolete, remove only those objects and then repack the surviving active islands; `nlAction=ignore` alone is not a readability cleanup.

## Derive Pin Exit Geometry From OA

For every master terminal, read the master symbol's actual pin figure or connection point and the relevant symbol bounds. Apply the instance origin, orientation, and complete transform to those master coordinates before creating visible geometry.

- Transform two points and subtract them when deriving a direction vector so translation is not mistaken for rotation or reflection.
- Determine the outward direction from transformed pin geometry, an explicit master pin direction when present, or the transformed symbol boundary. Do not derive it from device type, terminal name, or a remembered PMOS/NMOS convention.
- If a master has multiple pin figures or an ambiguous access point, resolve the actual connected figure from OA or require an explicit generator mapping. Stop rather than guess.
- Create an on-grid short stub in the derived outward direction. A stub is visible geometry, not permission to alter the electrical instance-terminal mapping.

## Route And Label

- Make same-block functional relationships visible with explicit local wires. An OA `instTerm` binding does not replace visible geometry, and a drawn wire or label does not replace a valid electrical binding.
- In a local current mirror or diode-connected reference branch, directly expose the reference drain-to-gate connection and the replicated gate trunk with one continuous netted route and real T-junctions when the symbols permit it. Do not split this relationship into same-name labels merely because OA already binds every terminal to the same net.
- Bind every generated or retained visible wire, path, and path segment to its intended OA net. A line that visually touches a connected terminal but reads back with `net=nil` is an orphan drawing error; cosmetic junction markers may remain netless only when they coincide with a verified real same-net branch point.
- Prefer continuous same-net trunks and real junction endpoints. Reject every ordinary different-net touch, crossing, shared endpoint, endpoint-on-segment contact, collinear overlap, or junction before creation and again from the complete in-memory geometry before save. Avoid wires through symbol bodies and long detours that obscure signal flow.
- After electrical binding, derive any generated label text exclusively from the connected `instTerm~>net~>name`. Do not invent a name from the planned role, symbol pin text, placement, or screenshot.
- Place a label on or immediately beside the actual netted wire near the relevant terminal or branch. Rotate a label to follow a vertical or horizontal route when that reduces clutter, and avoid adding an otherwise unnecessary extension solely to carry a label. Preserve enough clearance from instance names, parameters, pins, symbols, and other wires. Merge redundant labels on one visibly continuous local net; retain repeated labels only when distinct islands intentionally use the same global net name.
- **Net-name labels share one height** (user rule, 2026-09-18). Where the confirmed project grid is `0.0625`, every wire/net label uses height `0.0625`; mixed label heights are a defect. An audited cell held 122 labels at `0.125` and 77 at `0.0625` for the same class of net names, and normalising all 199 to `0.0625` kept the netlist and `schCheck` unchanged. Change the height of the existing label object (`label~>height`) instead of deleting and re-creating it, because a wire label carries its net name.
- Keep rail naming and placement consistent within the current design, while preserving separate power domains and avoiding an implied short between them.

## Keep Electrical And Drawing Objects Distinct

OA electrical terminals, pins, nets, and instance-terminal mappings are not interchangeable with labels, rectangles, lines, or text. A cosmetic object cannot create or delete an electrical interface.

When an authorized interface deletion is required, enumerate and update the electrical terminal/pin and every affected instance mapping or hierarchy consumer, then remove only the labels, rectangles, or other graphics that became orphaned. Conversely, deleting orphan graphics must not delete a still-required terminal. Use `$cadence-interface-contract-audit` when functional port classification or hierarchy-wide interface cleanup is part of the request.

## Enforce The Pre-Write Pin And Geometry Gate

Before opening the target appendable, derive immutable retained, moved, deleted, recreated, and master-changed pin sets from the frozen manifest and the complete mutation plan. A clear helper must exclude terminals, basic pin instances, pin figures, pin-owned displays, supply/ground nets, and all of their owned figures by identity. Any helper that iterates over all terminals, instances, shapes, or nets fails this gate when its reachable write set includes a protected boundary object; a later recreation is not preservation.

Read back the complete in-memory result before the first `dbSave` and require all of the following:

- protected pin delete, recreate, move, reorient, rename, master-change, net-change, and owned-figure drift sets are empty;
- every separately authorized pin migration matches its exact approved pin/view and coordinate or rule;
- supply and ground terminal identity, pin-to-net mapping, `sigType`, pin geometry, and owned display/stub/rail membership match the manifest, with no unintended power/ground merge or drift;
- every new or authorized moved object passes the numeric current-grid assertion;
- the complete unordered-pair set of transformed symbol-master BBoxes has no positive-area intersection; every collision record names both instances and masters and includes both BBoxes plus the intersection BBox;
- actual text and display bounds for new or authorized moved/edited content clear the neighboring symbols, pins, other text/labels, and unrelated wires; preserve intended own-wire label attachment. Unknown display bounds cannot pass, and protected legacy overlaps must be reported without moving protected objects;
- all different-net pin-figure and segment contact sets are empty, including supply-versus-ground touch, crossing, shared endpoint, collinear overlap, junction, and clearance violation.
- every junction has one same-net owner, and every conductive geometry connected component contains exactly one net identity/name, `sigType`, and power domain under the project-native connectivity semantics.
- every scalarized required input has exactly one contract-approved producer, every required output reaches exactly its approved consumers, no two required outputs drive one parent net, and every single-ended or no-consumer endpoint has an explicit named waiver.

If the generator cannot construct these sets or prove object ownership, stop before mutation; if a discrepancy first appears in memory, stop before save. A user's request to inspect the result manually or to omit post-write comparison cancels only that post-write work. It never cancels this preservation and geometry gate.

## Execute One Controlled Write

1. Reject or explicitly resolve unsaved edits before automation. Do not overwrite, auto-save, or silently merge an unknown interactive state.
2. Create a non-overwriting backup of the authoritative target and record SHA-256 for the backup files and baseline textual or structural evidence.
3. Re-read target identity, view-specific authorization, and the connectivity contract immediately before mutation. A planned symbol change that lacks the separate symbol confirmation is a hard stop, even when an automated helper could synchronize or regenerate it.
4. Before appendable access, load the exact helper closure and run a no-side-effect compatibility preflight in the bound CIW. Execute every read-only object/property accessor and late-assertion path against representative read-only objects; establish the current-runtime callable identity and expected signature of write, save, and reopen primitives without invoking their side effects. Unknown capability is a stop, and preflight does not prove that a later save will succeed. A runtime version, source search, or function name is not capability proof. Prefer exact unique matches from the live object's property collection over an unproven convenience lookup.
5. Apply the complete authorized placement, wire, label, and cleanup plan in one bounded SKILL/bridge transaction when OA is authoritative. Avoid repeated per-object round trips. For a batch of testbench sources, freeze one read-only plan and expected final signature, then use explicit `plan -> apply -> check/save -> reopen` stages from the linked transaction contract.
6. Maintain one append-only per-view save ledger and four explicit sets: `authorizedWriteSet`, `openedAppendableViews`, `modifiedViews`, and `savedViews`. Record exact `library/cell/view`, pre-write identity and backup/hash evidence, clean-state readback, appendable-open result, post-mutation modified-state readback, and each `dbSave` result. Add a view to `modifiedViews` only from actual readback and to `savedViews` only after its own successful save; never infer either set from the plan, an open call, a final marker, or another view's result.
7. On any error, stop and read back the partial state before deciding whether a bounded continuation is safe. When `savedViews` is empty, disk hashes still match the baseline, and the dirty in-memory object/property/mapping signature exactly matches the same operation's expected applied signature, do not replay instance or shape creation; continue only from the pre-save check stage with the same operation marker. A missing marker, signature mismatch, unknown session, or any successful save is a hard stop for automatic continuation. Do not continue stacking writes or loop indefinitely.

## Close Recovery By Exact View Set

Treat every restore or rollback as a new write transaction with new, exact view-level authorization. Derive `actualForwardSavedViews` only from the forward transaction's successful per-view save ledger, not from its authorized, opened, planned, or semantically related views.

Before recovery, bind each requested view to one exact pre-forward baseline or backup identity and hash, reopen the current target read-only, and check target identity, backup readability/hash, current content or structural hash, dirty/unsaved state, and user or concurrent drift. Unknown provenance, a dirty view, a hash mismatch, or unexplained drift stops that view; classify it as `driftedViews` or `unresolvedViews` and obtain a new user decision rather than overwriting it.

- `complete rollback` requires `requestedRecoveryViews == restoredViews == actualForwardSavedViews`, an empty `unresolvedViews`, and successful reopen/readback of every restored view against its bound baseline. Any excluded, retained, drifted, unproven, or unrestored forward-saved view makes the whole-forward rollback `partial`.
- `scoped recovery` is an explicitly authorized proper subset of `actualForwardSavedViews`. Label it exactly as scoped recovery, prove closure only for that requested subset, and list every forward-saved view outside the subset as retained/unrequested. It must not be reported as complete rollback; in whole-forward rollback accounting it remains partial.
- Sequential `dbSave` calls are not atomic. A script-level success marker cannot turn multiple view saves into one commit, and a mid-sequence failure leaves a partial saved set that must be reconciled from the ledger before any recovery plan is formed.

After recovery, close or release and reopen every restored view, read back the agreed electrical and drawing evidence, and report one row per `actualForwardSavedViews` member covering `forward saved | requested recovery | restored | retained | drifted | unresolved`. Empty or missing evidence is not a pass.

## Verify After Save

This is an evidence checklist, not authorization to execute every item. Honor explicit current-task exclusions of named post-write checks and mark them `not-run`; keep dependent connectivity or persistence claims `partial`. A review consumes available evidence and reports gaps without generating missing evidence. Pre-save pin-preservation and geometry checks remain mandatory and are not waived by a post-write exclusion.

1. Read back instances, origins, orientations, transforms, master terminal identities, `instTerm~>net~>name`, nets, visible wires, labels, terminals/pins, and orphan drawing objects.
2. Reuse the successful save already recorded in the per-view ledger; do not save again merely to verify it. Within the agreed persistence-check scope, close or release the edit view as appropriate, reopen, and repeat the structural readback so persistence is proven rather than inferred from a successful call. Unknown dirty state requires an explicit save/discard decision.
3. Run `schCheck` and applicable cross-view checks only when the user requests them or the agreed generation contract requires them. Treat them only as structural evidence.
4. Regenerate a fresh netlist from the changed authoritative OA and compare structured tuples such as `(instance, master terminal, net)` against the approved contract or pre-change baseline. Explain every intended difference and reject every unexplained terminal swap, missing connection, or added short.
5. Re-evaluate the scalarized endpoint-cardinality contract on that fresh netlist. Treat parent auto-net names, single-ended required inputs, no-consumer required outputs, duplicate required-output drivers, and any fanout delta as failures unless the exact endpoint is explicitly waived. Use `scripts/validate_spectre_hierarchy_contract.py` for Spectre netlists when its contract schema fits; it requires already scalarized instances, master ports, and nets and rejects unexpanded angle-bracket ranges in the checked parent. Contract `ports` may use range shorthand; scalar broadcast requires explicitly listing each scalar consumer in one relation. Rejection is unsupported input, not an electrical failure or authority to regenerate. Its static result does not replace the independent pre-save OA mapping gate.
6. For a before/after drawing review, compare two normalized views separately: electrical data such as masters, parameters, terminals, ports, and nets; and geometry data such as origins, orientations, wires, labels, junctions, and bounds. A zero electrical diff with a nonzero geometry diff is a drawing-only change, not a topology change.
7. Audit geometry using full visual bounds, not body-only BBoxes. Independently recompute the pairwise transformed symbol-master BBox set and reject every positive-area intersection, even when `schCheck` is clean; boundary-only contact is not an intersection. Also reject pin/body or text overlap, internal cells packed without functional-domain clearance, scalar nets drawn with bus/thick geometry, giant mostly empty generated symbols, a missing required symbol title, a symbol wider than the smallest on-grid width that clears its pin names and centered title, any left/right/top pin access center displaced from the body border, external pins stranded away from the nearest clear active-content perimeter, deleted-bank ghost slots, empty legacy frames or stale canvas holes, inconsistent signal-bank pitch or inside/outside label placement, power/ground pins spread across the full top width instead of a compact approved group, functional frames crossing or ambiguously enclosing objects, annotations detached from their frames, excess frame whitespace, crowded framed contents, avoidable different-net crossings, wires through device bodies, scattered functional groups, redundant labels, and any visible line/path/pathSeg whose OA net is nil.
8. Reject a producer level shifter whose confirmed outputs, including exemplar signals such as `G_P_DRV` and `G_N_DRV`, were changed from `output`/`opin` merely because a consumer analog interface is `inputOutput`; a `LEVEL_SHIFTER` supply template whose `VSS1`/`VDD1`/`VSS2`/`VDD2` mapping was inferred by order or name rather than read from real OA nets; or an `A`/`Q` digital-cell drawing that lacks short left/right horizontal exits, endpoint labels, and clear instance, master, and supply text.
9. Reject a local transmission-gate request that cleared or rearranged a protected analog exemplar, a rollback broader than the affected region or view without evidence that the broader scope was contaminated, or any repair reported without separate electrical and geometry diffs.

Report the backup and hashes, authorized write set, connectivity comparison, persistence readback, structural checks, readability findings, and all unverified claims. These checks do not prove simulation behavior, PVT coverage, DRC, LVS, reliability, or signoff; run those only when separately required and authorized.

For a reusable pre-generation or post-generation review, read and apply [the review prompt and checklist](references/review-checklist.md). When the request cites a user-approved correct example, also read [the compact functional-block style guide](references/compact-functional-block-style.md).
