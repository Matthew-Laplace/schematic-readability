# Cadence Schematic Generation And Readability Review

Use this reference to review a plan before generation or evidence after generation. Keep unknowns explicit and do not mutate OA during a review-only request.

All generic pitches below are subordinate to the entry Skill's Project Grid Overrides and the verified view grid. A confirmed project override is already an approved exception; do not request it again. Review checkboxes describe evidence, not execution authority. Honor explicit exclusions of named post-write checks as `not-run`, and keep dependent claims `partial`; do not generate missing netlists, reopen/save views, or run checks merely to fill the checklist. Mandatory pre-save protection and geometry checks are unchanged.

## Reusable Review Prompt

```text
Use $cadence-schematic-generation-readability in [pre-generation | post-generation] review mode.

Requested outcome:
[User-confirmed generation, reorganization, or review goal.]

Target identity:
[Current process/PDK, explicit bridge profile if live access is authorized, and target library/cell/view. Mark every unknown.]

Authorization:
- Read scope: [exact sources, netlists, OA views, logs, or reports]
- Write scope: [exact OA views/files, or "none"]
- Functional or simulation validation requested: [exact scope, or "none"]

Authoritative evidence:
- Intended topology or approved connection table: [path or inline table]
- Current fresh netlist: [path and provenance, or "not yet generated"]
- Current OA terminal mapping readback: [artifact or "not yet read"]
- Unsaved-edit status: [clean, unresolved, or unknown]
- Backup and baseline SHA-256: [artifacts or "not yet created"]

Review requirements:
1. Build or audit a table of instance, master, master terminal, actual/intended net, functional block, and allowed change. Treat current OA terminal mappings and a fresh generated netlist as electrical evidence; do not infer connectivity from screenshots.
2. If the user identifies a correct example, enumerate its protected instances, transforms, terminal mappings, local wires, junctions, labels, and bounds. Require adjacent work to leave this protected set unchanged unless a specific exception is authorized.
3. Check the placement plan by functional group, signal flow, power domain, and external interface bank. Require a full visual BBox for every object that includes body, pins, pin names, instance text, power pins, and stubs. Independently transform each authoritative symbol-master BBox into parent coordinates and compare every unordered instance pair: positive intersection width and height is a blocking symbol overlap, while edge-only or corner-only contact is not. Reject mechanically stacked TOP modules, a non-empty or incomplete symbol-overlap set, overlapping visual envelopes, internal standard cells or level shifters using `0.125` spacing, ambiguous rails, and avoidable crossings. Each symbol-overlap finding must name both instances/masters and both BBoxes plus the intersection BBox; `schCheck` cannot waive it. The `0.125` rule applies only to compact same-direction external pin banks.
4. If the request covers IO generally or says all pins, enumerate every schematic terminal and require each to map to a reviewed bank or explicit exception. Reject completion claims based on only one repaired bank.
5. Discover the same project's accepted scalar wire LPP/width and label style. Require ordinary thin wire for scalar nets, bus/thick geometry only for true multi-bit buses, and eight separate scalar wires for independent `STATE0` through `STATE7`. Reject a uniform physically wide `dbCreatePath` on every terminal.
6. For every new or changed symbol, first require separate current user confirmation for the exact `library/cell/symbol` and the proposed terminal/direction, bank/order, body, title/text, and parent-impact changes. Schematic, interface-cleanup, parent-wiring, or cross-view authorization cannot imply this write. Without symbol confirmation, perform only a read-only mismatch review. When authorized, identify the user-approved same-project exemplar and require dimensions that cover pin banks, the required title, and text without excess empty area, functional pin order, producer/consumer order consistency, access points on the boundary, pin figures outside, and pin names inside without overlap.
7. When functional frames are used, derive each frame from the final visible bounds of its owned circuitry, add consistent on-grid padding, and place one concise note immediately outside a consistent edge. Require non-electrical LPPs and reject oversized, intersecting, overlapping, ambiguous, or detached frame/note geometry.
8. Treat analog readability as a hard gate. Reject clearing a readable analog exemplar and mechanically stubbing every MOS terminal. For a segmented driver with the corresponding roles, require explicit `strong VCM`, `weak VCM`, `P fast`, `P slow mirror`, `P three-level protection`, `N fast`, `N slow mirror`, and `N three-level protection` islands.
9. Require explicit short local wiring for relationships inside current mirrors, differential pairs, cascoded branches, protection networks, switches, bias branches, and analogous same-block structures. Reserve net names mainly for cross-block or global networks, and require fast/slow branches, `PX`/`VO`/`NX`, parallel protection, and `VDD15` injection to remain directly traceable where present.
10. For every current mirror or diode-connected reference, require a continuous netted route from the reference drain to the shared gate trunk and replicated gates when direct wiring is practical. Require real junction endpoints at each branch.
11. Reject any visible electrical line, path, or path segment whose OA net is nil. A cosmetic junction dot may be netless only when it coincides with a verified same-net branch point.
12. For each visible terminal exit, require evidence that the master pin coordinate or access point and symbol bounds were transformed by the instance origin/orient/transform. Reject device-type guesses and any Computer Use rotate-by-Space workflow.
13. Check that generated stub labels are read from the connected instTerm~>net~>name after binding. Reject invented labels, unexplained terminal swaps, or any exchange of D/S/G/B or other terminals for aesthetics.
14. Check label clearance and consolidation. A label must sit on or near its actual netted wire, may rotate with the local route, and must not cover an instance name, parameter, pin, symbol, or wire. External terminal names must move with their pin figures, face the cell interior, and remain consistently aligned within the bank. Redundant labels and label-only extensions on one visible local net should be removed.
15. Distinguish OA electrical terminals/pins/nets/instance mappings from labels, rectangles, lines, and text. For any interface deletion, require both hierarchy-correct electrical cleanup and removal of only the graphics that became orphaned. Preserve the approved analog exemplar while removing only authorized obsolete digital objects.
16. After an authorized obsolete-terminal, ignored-instance, or disabled-island removal, require affected pin banks, functional islands, frames, and canvas bounds to be recomputed from surviving active content. Reject ghost slots, empty legacy frames, and stale blank bands.
17. Before an authorized write, require clean or explicitly resolved edit state, a non-overwriting backup, SHA-256 evidence, a complete write set, and one bounded bulk OA transaction. Stop on errors and inspect partial state before retrying.
18. After generation, compare normalized electrical and geometry snapshots separately, then require save/reopen structural readback and only the checks authorized for the task. Do not classify a geometry-only diff as a topology change.
19. Separate proven readability and connectivity facts from unrun simulation, PVT, DRC, LVS, reliability, or signoff claims.

Return:
- decision: approve, approve with required corrections, or reject;
- findings ordered by electrical risk and then readability impact;
- evidence for each finding, with exact artifact provenance;
- a functional-block placement and local/global routing assessment;
- terminal-mapping differences and any unexplained changes;
- required corrections within the authorized scope;
- validation completed, validation not run, and claims that remain unproven.
```

## Pre-Generation Checklist

- [ ] Target process/PDK, master symbols, current grid, target view, and explicit live profile are confirmed where applicable; none is inherited from another project.
- [ ] The requested function and connectivity contract are user-confirmed; missing requirements are reported rather than invented.
- [ ] Every instance terminal has an intended net and a verified master-terminal identity.
- [ ] Functional blocks, signal-flow order, power domains, repeated branches, and approximate bounds are planned before object creation.
- [ ] Every hierarchical module, standard cell, level shifter, and device has a planned full visual BBox covering body, pins, names, power pins, and stubs; TOP modules do not use mechanical fixed-increment stacking, and different internal functional domains have larger clearance than aligned peers within one domain.
- [ ] Every placed instance also has an authoritative symbol-master BBox transformed into parent coordinates; the complete unordered-pair set contains no positive-area intersection, boundary-only contact is not misclassified, and no protected existing object is scheduled to move merely to clear this gate.
- [ ] External pins are assigned to deliberate boundary banks with side, order, inward-facing label direction, one common row/column coordinate, and the confirmed project-grid-compatible pitch; `0.125` is only the generic default when compatible, not a universal override.
- [ ] `0.125` is used only for compact same-direction external pin banks, never as internal-cell or hierarchical-module spacing.
- [ ] The terminal inventory is complete: every schematic pin belongs to one reviewed bank or a documented exception; no untouched bank is hidden behind a partial completion claim.
- [ ] Each external access point lies on the intended symbol boundary, with pin figure outside and pin name inside; all pin, name, border, text, and neighboring-symbol clearances are non-overlapping.
- [ ] Every new symbol has a user-approved same-project exemplar, bounded dimensions without meaningless empty area, functional pin grouping, and producer/consumer order consistency.
- [ ] Every proposed symbol mutation has separate current user confirmation naming the exact `library/cell/symbol` and concrete terminal/direction, bank/order, body, title/text, and parent-impact changes. Without it, symbol mismatch review remains read-only and the symbol is absent from the write plan.
- [ ] Every user-approved correct example has an explicit protected-object set and exclusion bounds; no adjacent edit is allowed to disturb it.
- [ ] Each tightly coupled analog function is planned as a compact island with aligned equal-role devices, visible shared trunks, readable stacks, and neighboring parallel branches.
- [ ] A readable existing analog geometry or backup remains protected during interface migration or digital-cell deletion; the plan does not clear all analog shapes or fan every MOS terminal into isolated stubs.
- [ ] Where applicable, the eight segmented-driver islands are explicit and the fast/slow, `PX`/`VO`/`NX`, parallel protection, and `VDD15` paths are directly traceable.
- [ ] Every planned functional frame has one owned island, final-content-derived bounds, consistent on-grid padding, a concise adjacent note, and a non-electrical LPP; frames are added only after internal placement and routing are readable.
- [ ] Local same-block relationships use explicit wires; cross-block/global networks use deliberate labels.
- [ ] The project's accepted scalar wire LPP/width and label style are recorded; scalar nets use ordinary thin wires, only true multi-bit buses use bus/thick geometry, and independent one-hot states remain separate scalar wires.
- [ ] Current-mirror reference drain, shared gate trunk, and replicated gates use one direct netted route with explicit branch points when practical.
- [ ] Every planned visible electrical line/path/pathSeg will be assigned to its intended OA net; cosmetic junction markers are distinguished from electrical routes.
- [ ] Pin exits will be derived from transformed master pin geometry, not device stereotypes or GUI rotation.
- [ ] Label text will come from actual `instTerm~>net~>name` after electrical binding.
- [ ] Terminal assignments, including D/S/G/B when present, are frozen against readability-only swaps.
- [ ] Label clearance, branch spacing, rail clarity, snap/grid, and compact non-overlap constraints are defined from the current design.
- [ ] Unsaved edits are absent or explicitly resolved; backup, SHA-256, write set, bulk transaction, and error stop conditions are ready.
- [ ] Authorized removals of obsolete terminals, ignored instances, or disabled islands trigger a fresh compact placement and bank plan with no ghost slots, empty legacy frames, or stale canvas holes.
- [ ] Post-save structural readback, reopen, cross-view/`schCheck`, and fresh-netlist comparison criteria are defined.

## Post-Generation Checklist

- [ ] Backup identity and SHA-256 evidence predate the write.
- [ ] Actual changed objects stay within the authorized write set.
- [ ] Every changed symbol had its own current exact symbol authorization; no schematic, interface, parent, or cross-view operation was used as implicit permission.
- [ ] Protected exemplar instances, transforms, terminal mappings, local wires, junctions, labels, and bounds are unchanged.
- [ ] Reopened OA mappings match the approved `(instance, master terminal, net)` contract, with every difference explained.
- [ ] No terminal was exchanged for placement or appearance.
- [ ] The independently recomputed transformed symbol-master BBox pair set has no positive-area intersection; each failure, if any, reports both instance/master identities, both BBoxes, and the intersection BBox, and a clean `schCheck` is not treated as a pass. Full visual BBox checks separately show that TOP modules, internal cells, pins, names, power pins, and stubs do not collide; peer cells align within a function and different functional groups retain larger clearance.
- [ ] Functional groups are compact, readable, consistently aligned, and separated by signal flow or power domain as planned.
- [ ] Functional frames contain all and only their owned visible objects, use consistent minimal padding, do not cross or overlap electrical geometry or peer frames, and have concise notes attached to the intended edge.
- [ ] Framed circuitry has no avoidable blank area or collisions among symbols, instance names, parameters, pin names, net labels, junctions, and wires.
- [ ] External pins form compact rows or columns with the measured approved project-grid-compatible pitch (`0.125` only when applicable); no bank is stretched across internal functional-band heights, no pin remains stranded in empty canvas, and terminal name/direction/net/pin identity are unchanged. Reuse an already confirmed project override.
- [ ] No internal standard cell, level shifter, or hierarchical module uses the external-bank `0.125` pitch as its spacing rule.
- [ ] New or changed symbols match their approved same-project exemplar, retain the required identifying title, contain pin banks and text without excess empty area, preserve functional pin order, and keep access points on the boundary, pin figures outside, and names inside without collision.
- [ ] The post-generation bank report accounts for every terminal and lists each bank's members, common coordinate, pitch, and exceptions.
- [ ] Directly related devices do not contain avoidable blank rows or columns; repeated gaps are consistent and remain large enough for current symbol, text, pin, wire, and label clearance.
- [ ] Removed terminals or disabled objects left no ghost pin slots, empty legacy frame, inactive hole, or stale page-scale extent; surviving active islands and banks were recomputed.
- [ ] Same-block relationships are visibly connected with short continuous local wires; global labels are not being used to conceal local topology.
- [ ] Scalar nets match the project's ordinary thin-wire and label style; no scalar or one-hot state net is drawn as a bus/thick path, and no uniform physically wide `dbCreatePath` pattern remains.
- [ ] Analog readability passes as a hard criterion: approved old MOS geometry and mirror relationships remain intact, required functional islands are explicit, and fast/slow, `PX`/`VO`/`NX`, protection, and `VDD15` paths are traceable where applicable.
- [ ] Current-mirror reference drain and shared gates form one visibly continuous netted route with real junction endpoints.
- [ ] No visible electrical line/path/pathSeg in the edited region reads back with `net=nil`.
- [ ] Stub direction follows transformed master pin geometry, and all checked connection geometry is on the active grid.
- [ ] Labels use actual OA net names, sit on or near their wire endpoints, follow local route orientation where useful, avoid collisions, and contain no needless duplicates or label-only extensions; terminal-name displays face inward and align consistently with their boundary pins.
- [ ] Electrical and geometry snapshots were compared separately; every reported topology change is supported by a master, parameter, terminal, port, or net difference.
- [ ] Electrical terminals/pins and cosmetic graphics are both present or removed according to intent; no orphan interface graphics remain.
- [ ] Save/reopen readback, cross-view checks, `schCheck`, and a newly generated netlist comparison completed without unexplained errors.
- [ ] Simulation, PVT, DRC, LVS, reliability, and signoff are reported as unproven unless independently run under an explicit requirement.
