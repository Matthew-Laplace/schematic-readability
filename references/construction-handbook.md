# Construction Handbook: How To Build A Readable Schematic

This handbook records the **procedure**. `SKILL.md` records the **rules** - what
must hold, and what authorization each write needs. When the two appear to
disagree, `SKILL.md` and its Save Acceptance Gates win.

Read this handbook end to end once before your first construction. After that,
use the phase index and the cookbook in section 10.

**Phase index**

| Phase | Name | Output |
|---|---|---|
| 0 | Freeze before drawing | a frozen connectivity contract and a declared write set |
| 1 | Read the circuit | an island decomposition, a flow direction, symmetry axes |
| 2 | Budget the canvas | absolute coordinates for every instance |
| 3 | Place | instances on the lattice, non-overlapping |
| 4 | Route | bound, thin, orthogonal geometry |
| 5 | Annotate | labels, frames, notes |
| 6 | Verify | two gates, a score, a render review |
| 7 | Deliver | a two-layer report |

Phases are ordered for a reason. Most unreadable schematics are the product of
starting at phase 3.

---

## 1. The Model: Readability Is Recoverability

A schematic is not the circuit. It is a **lossy visual encoding** of a netlist,
and the reader's job is to decode it back into the netlist. Everything in this
handbook follows from one definition:

> **A schematic is readable to the degree that a competent engineer can
> recover the intended netlist from the picture quickly and without error.**

This is why the rules are what they are. Each rule suppresses a specific,
identifiable decoding failure:

| Visual property | Decoding failure it prevents |
|---|---|
| Non-overlap | illegible - two objects claim the same pixels |
| Grid alignment | misread connection - a wire that looks attached but is not |
| Orthogonal routing | ambiguous path - the eye cannot trace a diagonal reliably |
| No wire through a body | false membership - a wire appears to belong to a device it does not |
| Explicit junctions | ambiguity - is this a crossing or a connection? |
| Functional grouping | search cost - the reader must scan the page to find related devices |
| Symmetry | pattern cost - a differential pair that is not mirrored reads as unrelated |
| Consistent label height and placement | false hierarchy - varying type reads as varying importance |
| Complete terminal visibility | false negative - an unshown connection reads as no connection |

Two consequences worth stating plainly:

1. **Electrical correctness and readability are independent axes.** A drawing
   can be electrically perfect and unreadable, and a beautiful drawing can be
   electrically wrong. They need separate checks, and this handbook keeps them
   separate.
2. **Readability has a cost budget.** Every wire adds decoding work. The goal is
   not "more explicit is always better" but "explicit where the relationship
   matters, grouped where it does not".

### The four layers

Work them in order. A later layer cannot compensate for an earlier one.

| Layer | Content | Character |
|---|---|---|
| 1. Electrical truth | devices, terminals, nets, port directions | invariant - never changes for appearance |
| 2. Functional structure | which devices form which function, flow direction, symmetry | derived by reading the circuit |
| 3. Geometry | placement, orientation, wires, junctions | the search space |
| 4. Presentation | labels, frames, notes, typography | the finishing layer |

If you find yourself adjusting layer 3 to fix a layer 2 mistake, stop and go
back to phase 1.

---

## 2. Phase 0 - Freeze Before Drawing

Nothing is drawn in this phase. Its purpose is to make every later decision
checkable.

### 2.1 Establish the connectivity contract

Produce a table with at least these columns, one row per instance terminal:

```text
instance | master | master terminal | intended net | functional block | allowed change
```

For an existing design, derive it from the **current netlist and current OA
mappings**, not from a screenshot and not from memory. For a new design, derive
it from the user-confirmed requirements and the approved master terminal
definitions.

Then freeze the following, separately:

- the boundary port set, with names **and** directions;
- the net count;
- the complete label inventory if labels already exist (text, height,
  orientation, justification, position);
- the endpoint-cardinality contract: for each required input, its one legal
  driver; for each required output, its exact consumer set.

Expand instance arrays into their real elements and bus terminals into scalar
bits before freezing. A device `m` parameter is not an instance array.

### 2.2 Confirm the grid

Record the coordinate quantum, the pin-bank pitch, the label height, whether
half-grid is permitted, and the origin that "on grid" is measured against.

A project-confirmed grid overrides every generic default in `SKILL.md`. If the
grid cannot represent the planned lattice, report the incompatibility instead of
changing view settings.

### 2.3 Identify the exemplar, if one exists

If the user has marked a region as correct, convert that approval into an
explicit **protected set** before touching anything: instances, origins,
orientations, terminal-to-net mappings, local wires, junctions, labels, and the
bounds needed to keep adjacent edits out. Record it as
`object | identity | geometry | electrical mapping | protected scope`.

### 2.4 Bind the authorization

Name the exact `library/cell/view` targets. A schematic write is not permission
to touch a `symbol` view. A read-only or audit request ends here.

### 2.5 Back up

Non-overwriting backup of the authoritative target, with the baseline evidence
you will need to prove the change later. Do not proceed on an unknown or dirty
edit state - resolve it first.

**Exit condition for phase 0:** a frozen contract, a confirmed grid, a declared
write set, and a readable backup. If any is missing, stop.

---

## 3. Phase 1 - Read The Circuit Before Drawing It

This is the phase that most automation skips, and skipping it is why automated
schematics look like netlists with symbols.

Drawing is a rendering problem; reading the circuit is a **structure
recognition** problem. Do the recognition first, then render.

### 3.1 Inventory devices and rails

Build three sets:

- **Devices**, with terminal maps and types.
- **Rails** - nets that are supplies or grounds. Identify them from the design's
  own conventions and the confirmed contract, then confirm by connectivity: a
  rail is a net that many devices reference and that has no ordinary signal
  driver. Keep distinct power domains distinct; never merge them visually or
  electrically.
- **Ports** - the cell boundary terminals, with directions.

### 3.2 Recognize the structural idioms

Do not place devices one at a time. Recognize the idioms first - they are the
units of readable placement. Section 10 gives detection signatures and
placement recipes for each:

`differential pair` | `current mirror` | `cascode stack` | `tail source` |
`output stage` | `level shifter` | `transmission gate` | `bias ladder` |
`protection network` | `digital cell`

Every idiom you find tells you two things: which devices must be adjacent, and
which relationships must be drawn as wire rather than left implicit.

### 3.3 Decompose into functional islands

A **functional island** is the smallest set of devices that

- share at least one local net that is meaningful to the reader, and
- whose relationships would be unclear if the devices were separated.

Grow islands by this rule:

1. Seed an island with each recognized idiom.
2. Merge two islands if they share a net that is neither a rail nor a
   top-level port.
3. Stop merging when the island exceeds roughly 16 devices, or when the shared
   net is only a rail.

Devices that belong to no idiom and share only rails form their own small
islands. Do not force them into a neighbour's island merely to fill space.

### 3.4 Determine flow direction

Establish the reading order:

1. Where do the inputs enter? Where do the outputs leave?
2. Trace the forward path from input to output through the device graph.
3. The dominant direction of that trace is the flow axis - conventionally
   left to right, or top to bottom for a stack-dominant design.
4. Feedback paths run **around the perimeter** of the island, not back through
   it. A feedback wire that cuts across the forward path is a decoding hazard.
5. Bias and reference branches sit off the flow axis, typically below or to one
   side, so they do not compete with the signal path for attention.

### 3.5 Determine symmetry axes

For each matched group - differential pair, current mirror, cascode pair,
complementary branches - record:

- the member devices,
- the axis or centre line,
- which members are mirror images of which.

**The axis is supplied, never inferred.** If the circuit contains a symmetric
structure but the axis is not obvious from the confirmed structure, stop and ask
rather than guessing from net names.

### 3.6 Assign the power and ground convention

Decide and record, for this design:

- supply rails at the top, ground at the bottom (or the project's confirmed
  alternative),
- which rail feeds which island,
- where separate domains must stay visually separate to avoid implying a short.

**Exit condition for phase 1:** a list of islands with their member devices and
bounds; a flow direction; a set of symmetry axes; a rail and port inventory.
Every one of these is a *derived* fact, traceable to the netlist.

---

## 4. Phase 2 - Budget The Canvas

Convert structure into coordinates. Still no drawing objects exist.

### 4.1 Compute full visual bounds per instance

A body-only box is not a placement envelope. Build the union of:

- the transformed symbol-master body outline;
- every pin figure and pin access point;
- pin names;
- the instance name;
- parameter or value text;
- power and ground pins;
- any planned stub or label that belongs to the instance.

Add explicit clearance. This union plus clearance is the **envelope** you place
against.

### 4.2 Size the islands

For each island, pack its members on the lattice using the per-structure spacing
rules (section 10) and the confirmed grid. Then take the union of the member
envelopes as the island envelope.

Prefer the **nearest on-grid spacing that clears all envelopes**. Do not insert
empty rows or columns "for room" - unused space increases the reader's eye
travel for no benefit. Do not compress below clearance to save area - collisions
are a hard failure.

### 4.3 Lay out islands

Place islands along the flow axis in signal order. Between islands, leave a
visibly larger gap than the intra-island spacing so the boundary is
unambiguous.

### 4.4 Decide whether to split

Split when any of these hold:

- an island exceeds the practical device budget;
- more than one independent signal domain must be shown;
- the drawing cannot stay legible at the deliverable size.

When splitting, keep cross-sheet relationships as **matching net names with
visible ports**, never as long wires that span the page or leave it.

### 4.5 Snap, then re-check

Snap every planned coordinate to the lattice, then re-run contact analysis on
the snapped plan. If snapping introduced a touch, a merge, or any topology
change, stop - the plan is wrong, not the grid.

**Exit condition for phase 2:** absolute on-grid coordinates for every instance,
with verified clearance and no topology change introduced by snapping.

---

## 5. Phase 3 - Place

Now create instances. One bounded, authorized batch.

### 5.1 Order of placement

1. Rails and their anchors.
2. Each island's spine - the devices that carry the signal path.
3. Symmetric partners, placed as exact mirror pairs about the recorded axis.
4. Support devices - bias, protection, decoupling - adjacent to what they serve.
5. Boundary pins last, after the content they connect to has settled.

### 5.2 Placement rules that apply everywhere

- **Non-overlap is a hard invariant.** Test the complete unordered-pair set of
  transformed envelopes. Positive width *and* positive height is an overlap;
  edge-only or corner contact is not.
- **No fixed-increment stacking.** Two hierarchical instances must not be placed
  at a mechanical constant offset; place from their actual envelopes.
- **Orient by geometry, never by convention.** Choose rotation or mirroring so
  that the terminals that must connect are the ones facing the connection.
  Derive this from the transformed pin positions, not from "PMOS usually points
  this way".
- **Never exchange terminals for appearance.** Preserve D/S/G/B. A cleaner
  drawing with an unexplained terminal change is a failed result.
- **Keep equal-role devices aligned.** Devices in the same role share a row or
  column.
- **Series devices stack along the flow direction; parallel alternatives sit on
  adjacent tracks.**

### 5.3 Boundary pins

Place the electrical access point **exactly on the symbol body border**, the pin
figure outside, the pin name inside.

Group same-direction pins into one compact bank on one side, with one shared
boundary coordinate and a consistent pitch. Choose the side from interface role
and signal flow. Do not spread a bank to align each pin with its distant internal
block - preserve that association through pin order and naming instead.

**Exit condition for phase 3:** every instance placed, oriented, and
non-overlapping; boundary banks complete; no terminal changed.

---

## 6. Phase 4 - Route

### 6.1 Derive escapes from real geometry

For each terminal, read the master's actual pin figure, apply the instance's
complete transform, and take the two transformed points to get a direction
vector. Determine the outward direction from that geometry - not from the
device type, the terminal name, or a remembered convention.

If a master has multiple pin figures and no unambiguous access point, stop and
resolve it rather than guessing.

### 6.2 Decide: wire or label

Apply this rule in order:

| Condition | Choice |
|---|---|
| Both endpoints are inside one island, and a short orthogonal route exists | **draw the wire** |
| The relationship defines the function (mirror gate trunk, diode-connected reference, diff-pair source) | **draw the wire**, even if a label would be shorter |
| The connection crosses islands, or the route would have to run a long way | **use a matching net name** on ports or short stubs |
| The net is a rail | use the rail, with a short stub at each tap |

The underlying principle: proximity and relationship should be visible. A local
relationship expressed only by repeated labels forces the reader to perform a
text search across the drawing.

### 6.3 Build trunks and branches

For a net with several taps inside one island, run **one trunk** with real branch
points, rather than several isolated segments that happen to share a name.

Junction discipline:

- attach branches at true T points;
- never create a four-branch point carrying a solder dot - it is a warning-level
  defect, and the accepted repair is to split it into two three-way T junctions
  by stepping one branch one grid step aside;
- every junction must resolve to exactly one net identity.

### 6.4 Keep geometry thin and orthogonal

Create every connection as a width-0 line. A width-carrying wire, a
`dbCreatePath`, or a thick bar used to bridge a gap is a defect - with one
caveat: a legacy wide wire may be **load-bearing** because it owns the label that
names its net. Deleting such a bar deletes the net name. Convert it by
recreating the thin wire and re-gluing the label to the real new wire id, and
verify the net count afterwards.

Route only horizontally and vertically. A diagonal segment is not merely
unfashionable - it makes "is this attached?" a judgement call.

### 6.5 Avoid, and check contact

- A wire must not pass through a symbol body.
- Preferred avoidance: leave from the pin, step to a clear lane outside the
  obstacle's bounding box, travel along it, step back in. Take the shortest such
  detour; do not loop around the far side.
- Distinct nets must share no endpoint, no endpoint-on-segment contact, no
  T-intersection, no collinear overlap, and no foreign-pin intrusion.
- A different-net visual crossing is permitted only where the project's native
  non-connecting crossing semantics are confirmed. Ordinary crossing lines are
  not an inferred exception.

### 6.6 Bind every wire

Every visible electrical line, path, and path segment must read back with its
intended OA net. A line that visually touches a terminal but reads `net=nil` is
an orphan drawing error, not a cosmetic issue.

**Exit condition for phase 4:** every terminal visibly covered; every wire
bound; zero different-net contacts; zero wire-through-body; zero four-way
dotted junctions.

---

## 7. Phase 5 - Annotate

Annotation is what makes the structure legible at a glance. It is also the most
common source of new defects, because text is placed after geometry and can land
on top of it.

### 7.1 Net labels

- Text comes **exclusively** from the connected net's actual name. Never invent
  a label from the planned role, the pin text, or a screenshot.
- Place the label on or immediately beside its own wire, near the terminal or
  branch it explains.
- One class of label, one height. Mixed heights read as mixed importance.
- Preserve clearance from instance names, parameters, pins, and other wires.
- Merge redundant labels on one visibly continuous local net. Keep repeated
  labels only where distinct islands intentionally share a global net name.

### 7.2 Instance text

Normalise reference and value text to horizontal, left-to-right reading order as
a by-product of placing or moving the instance - not as a separate cleanup pass.
Collision boxes must include the text margin, not just the symbol body.

When a sheet is dense, demote the least informative text: hide eligible passive
values and collect them in a parameter block below the drawing. Keep source
waveforms and active-device model names visible; those carry meaning that the
reader needs in place.

### 7.3 Frames and notes

- One frame per meaningful island, drawn from the **final** union of its
  contents plus consistent on-grid padding.
- Frames and notes go on a non-electrical layer and carry no net.
- One short note per frame, on a consistent outside edge, naming the block or
  its engineering role.
- A frame must not cross symbols, wires, labels, or another frame's boundary.
- A note must never cover geometry, and never substitute for drawing a
  relationship explicitly.

**Exit condition for phase 5:** all text legible, no text-over-geometry, one
height per label class, frames derived from final content.

---

## 8. Phase 6 - Verify

Four independent checks. Do not merge them into one verdict.

### 8.1 Gate 1 - the netlist did not change

Take the same-cell electrical snapshot and require an exact match against phase
0: every `(instance, terminal) -> net` tuple, the net count, and the boundary
port set with names and directions.

A zero electrical diff with a non-zero geometry diff is a drawing-only change -
that is the normal, acceptable outcome.

If a readability goal cannot be reached without moving a terminal to another
net, splitting a net, or creating one, **stop and report the conflict**. Never
save such a change as "readability".

### 8.2 Gate 2 - warning-free

Run the check against the exact state that will be written and require zero
errors **and** zero warnings before saving.

Floating, dangling, or unused wires and labels are defects to fix, not noise to
accept. Deleting an unused stub is safe only if the net name is still produced
by a retained label or by the confirmed contract - re-verify net names and net
count afterwards.

A clean check is necessary but not sufficient: it does not prove netlist
identity, geometry non-overlap, or function.

### 8.3 Geometry review

Recompute, on the final state:

- every pairwise transformed envelope - no positive-area intersection;
- text and label bounds against symbols, pins, and unrelated wires;
- every terminal's visible coverage;
- every junction's single net owner;
- the endpoint-cardinality contract against a fresh netlist.

### 8.4 Score and render

Compute the readability score for a breakdown and a `worst_category` pointer.
Then **look at the rendered drawing**. The score is a fast proxy; the render is
the ground truth. A clean diagnostic result will not reveal a crowded layout, a
poorly aligned label, or a legal but confusing crossing.

Inspect the render for: legible non-overlapping text; consistent spacing;
thin wires with small junctions; no region too dense to trace a net; nothing
clipped; crossings unambiguous; islands visually separable; flow followable.

**Stopping rule:** stop when a full repair pass produces no applicable change,
even if the score is below target. The remaining gap needs human judgement.

---

## 9. Phase 7 - Deliver

Report the two layers **separately, in this order**:

1. **Gates** - netlist identity and the check result, with the evidence that
   actually passed. State that a clean check is necessary but not sufficient.
2. **Score** - total, per-category breakdown, worst category.
3. **Render review** - what was inspected, what changed, what remains.
4. **Unverified** - anything resting on an estimated-text model, anything that
   was a render-only judgement, and any finding left open because no repair
   applied.

Then the boundary facts, stated as three separate things rather than one:

- what was analysed;
- what was written;
- what was verified, and to which level.

Use `verified` / `partial` / `blocked` / `not-run` explicitly. "The command ran"
is not a completion claim; "the file exists" is not a functional claim.

---

## 10. Structural Cookbook

Detection signatures and placement recipes. The signatures are heuristics over
the connectivity graph - confirm each against the actual netlist.

### 10.1 Differential pair

**Signature.** Two devices of the same type and comparable size, sharing source
net `S`, with drains on two distinct nets and gates on two distinct nets; plus
exactly one other device whose drain is `S`.

**Axis.** Perpendicular to the line joining the two devices, at its midpoint.

**Recipe.**

- The two devices are exact mirror images about the axis, at equal spacing.
- Corresponding terminals face the axis or the shared trunk - not away from it.
- The gate nets leave on the outside, in the flow direction.
- The tail device sits below the common source node (for NMOS), on the axis,
  with a short symmetric connection to both sources.
- Do not mirror one member and leave the other unmirrored merely because the
  symbol happens to face that way.

**Routing.** The tail connection is a real T: one trunk from the tail drain to
the midpoint, then two short symmetric branches. This is a case where a label
would be wrong even though it is shorter.

### 10.2 Current mirror

**Signature.** Two or more devices of the same type sharing a gate net `G`;
exactly one of them has drain net equal to `G` (diode-connected). The others'
drains are outputs.

**Recipe.**

- Reference (diode-connected) and replicas sit side by side on one row.
- The gate trunk runs continuously between them.
- The reference's drain-to-gate connection is drawn as one continuous route,
  visible, not replaced by matching labels.
- The one that is mirrored is a **geometry** decision: mirror whichever member
  needs its terminals facing the shared trunk. Do not carry a "left is R0"
  rule across symbol libraries.

**Routing.** One trunk, real branches, no label-only representation of the
mirror relationship.

### 10.3 Cascode stack

**Signature.** Device A's drain connects to device B's source; B's gate is a
bias net; chain length two or more.

**Recipe.**

- Stack along the flow direction - the series order is the reading order.
- All gates of the cascade share one compact bias rail, drawn once.
- The stack's input at one end, output at the other, so the reader can follow it
  top-to-bottom or left-to-right without backtracking.

### 10.4 Tail source

**Signature.** A device between a diff pair's common source node and a rail (or
another bias node).

**Recipe.** On the axis, below (for NMOS) the pair, with a symmetric fan-out to
the pair's sources. Its own gate is a bias input, routed on the outside.

### 10.5 Output stage

**Signature.** A device whose drain is a top-level output net.

**Recipe.** Shift it toward the output edge of the flow. Keep its gate
connection to the preceding stage as a short, direct wire - this is the
relationship the reader most needs to see.

### 10.6 Level shifter

**Signature.** Cross-coupled pairs in two different supply domains; two distinct
supply nets.

**Recipe.**

- The two supplies are never merged visually. Distinguish them by explicit net
  names on their own stubs.
- Each supply gets its own stub, uncrossed, in a compact group.
- Cross-coupled connections are drawn as real wires forming the visible
  cross - that cross *is* the function.
- Producer and consumer keep their own verified port directions. Do not
  propagate a consumer's direction backward into the producer merely because
  they share a net.

### 10.7 Transmission gate

**Signature.** Parallel NMOS and PMOS with complementary gate drives and shared
source/drain nets.

**Recipe.** One standard grammar per project: the two devices adjacent, the two
gate controls entering from opposite sides or from a marked control pair, and
the pass path drawn as one continuous horizontal line through both. Do not
invent a new arrangement per instance.

### 10.8 Bias ladder

**Signature.** A series chain of devices between two rails with taps feeding
other islands.

**Recipe.** Vertical stack, equal spacing, taps leaving horizontally to the
right or left toward their consumers. Keep it out of the signal path.

### 10.9 Protection network

**Signature.** Devices connecting a protected node to a rail, or across two
nets, with a clamp or limiting role.

**Recipe.** Adjacent to the node they protect, with the protected-node path
visible. Do not park protection devices in a corner detached from what they
protect.

### 10.10 Digital cell

**Signature.** A cell with input `A` and output `Q` and no analog structure.

**Recipe.** Input exits horizontally to the left, output horizontally to the
right, from their transformed access points. Net names at the outer end of each
line, not piled under the device. Instance name, master name, and supply names
stay visible with clearance.

---

## 11. Failure Catalog

Each row is a defect actually observed during construction work, with how it
manifests and how to detect it early.

| # | Symptom | Root cause | Detection | Repair |
|---|---|---|---|---|
| 1 | Net count balloons; hundreds of floating warnings | A wide wire was deleted, and it owned the label that named the net | Compare label inventory before/after, not just connectivity | Recreate the thin wire, re-glue the label with a real wire id, re-verify net count |
| 2 | Label re-creation fails silently with `SCH-1001` | The wire-creation call returned a **list** of ids, and the list was passed as the glue argument | Assert the return type before using it as a glue target | Extract the real id, then glue |
| 3 | Check reports a solder dot on a crossover | Four branches meet at one dotted point | Warning count is non-zero | Step one branch aside by one grid step to make two T junctions |
| 4 | Wire looks attached but the net does not include the pin | Endpoint missed the pin, or the geometry reads `net=nil` | Read back the net of every drawn line | Move the endpoint exactly onto the pin; re-bind |
| 5 | Two different nets touch | Shared endpoint, endpoint-on-segment, collinear overlap, or a clearance envelope collision | Pairwise contact check across distinct nets | Reroute; do not "fix" it with layer or color |
| 6 | Instances overlap only in the text | Body-only bounding boxes were used | Compare full visual envelopes | Re-place using envelope + clearance |
| 7 | Symbol body too wide, mostly empty | Body sized from port count instead of an approved exemplar | Compare against the project's approved symbol | Re-derive from the exemplar's proportions |
| 8 | Mirror reads as two unrelated devices | One member mirrored, the other left as-is | Check handedness of the pair about the recorded axis | Mirror the correct member |
| 9 | Terminal silently swapped | Orientation chosen by convention instead of transformed pin geometry | Diff the `(instance, terminal) -> net` tuples | Revert; re-derive orientation from geometry |
| 10 | Readable analog block replaced by isolated stubs | A "cleanup" pass cleared geometry it was not authorized to touch | Compare protected-set membership | Restore from backup; re-apply only the authorized scope |
| 11 | Legacy off-grid pin silently moved | A snap pass treated a protected pin as ordinary geometry | Check protected pins against baseline coordinates | Restore; report the baseline condition instead |
| 12 | Frames overlap or enclose foreign objects | Frames drawn from planned bounds rather than final content | Recompute frames from the final union | Redraw after content settles |
| 13 | Labels collide after a move | Text moved with the object but was not re-normalised | Render and inspect | Normalise text orientation and offsets |
| 14 | Dense sheet where one net cannot be traced | No annotation downgrade, or no split | Render review; density check | Demote passive values to a parameter block, or split the sheet |

Three cross-cutting lessons from this table:

1. **Most catastrophic defects are geometry-driven, not electrical-logic-driven.**
   The intent was fine; the coordinates were not.
2. **The dangerous failures are silent.** A missing label, a lost net name, a
   dropped id - none raise an error at the moment they happen. Only an explicit
   before/after comparison catches them.
3. **Protection is a scope problem, not a technique problem.** Nearly every
   destructive incident came from an operation that was individually reasonable
   but applied more broadly than authorized.

---

## 12. Numbers Card

Values are grouped by their own units; **do not compare across groups**.

### Lattice and spacing

| Item | Value | Note |
|---|---|---|
| Coordinate quantum | `0.0625` | confirmed project value |
| Pin-bank pitch | `0.125` | two quanta; compact same-direction external banks only |
| Label height | `0.0625` | one height per label class |
| Planning step | `1.5` | 24 quanta - a spacing proposal, not a legal constraint |

### Geometry predicates

| Predicate | Threshold |
|---|---|
| Overlap | positive width **and** positive height |
| Counted overlap area | at least `1.0` (scaled) - below this a graze is legal |
| Off-lattice | deviation greater than a small tolerance from the nearest lattice point |
| Diagonal | both `dx` and `dy` non-zero |

### Estimated text box

```text
width  = len * font * 0.66        (bold multiplies width by 1.12)
height = font
```

An estimate - mark findings derived from it as estimated.

### Scale and splitting

| Circuit size | Guidance |
|---|---|
| comfortable island | up to ~16 devices |
| consider splitting | more than ~20 devices, multiple signal domains, or more than one feedback loop |
| ground symbols | few - share a bus; many (roughly 16+) - individual symbols |

---

## 13. What This Handbook Does Not Do

- It does not establish that the circuit is functionally correct. It governs the
  drawing, not the design.
- It does not prove a simulation, DRC, LVS, or signoff result.
- It does not authorize any write. Authorization lives in `SKILL.md` and is per
  view.
- It does not make a score a verdict. The score orders your attention; the
  rendered drawing is the ground truth.
- It does not transfer project conventions between processes. A PDK change or a
  new project invalidates the exemplar-derived rules and requires fresh
  calibration.

Use it as the procedure, `SKILL.md` as the contract, and the render as the
evidence.
