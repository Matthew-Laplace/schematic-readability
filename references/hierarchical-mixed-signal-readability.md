# Hierarchical Mixed-Signal Schematic Readability

Use this reference when a schematic combines hierarchical modules, digital control, level shifters, transmission gates, and analog device islands. It defines a cross-process visual grammar. The current netlist, OA terminals, master-terminal definitions, and `instTerm`-to-net mappings remain the electrical authority.

This grammar controls presentation only. Never change a terminal assignment, net, device parameter, hierarchy contract, or topology to make the drawing fit.

`EXAMPLE_SYMBOL` is a confirmed same-project geometric and stylistic exemplar case for this grammar. Copy its visual syntax and relationships when selected for the current project; do not require that cell in another process, copy its absolute dimensions, or treat its name as a portable PDK object.

## Freeze The Facts Before Placement

Record these inputs before generating or reorganizing geometry:

- every instance master, origin, orientation, and transformed terminal access point;
- every schematic terminal, symbol pin, parent instance terminal, direction or electrical role, and real OA net;
- each hierarchical module's complete visible envelope, including symbol body, pin figures, pin names, instance name, properties, power terminals, stubs, labels, and owned annotations;
- the same-project approved scalar wire, true-bus, label, symbol, pin, frame, and annotation conventions;
- all power and body terminals that require visible supply treatment;
- any user-approved red-boxed, white-boxed, or otherwise identified correct region that must be protected.

Do not infer any of these facts from screenshot position, array order, a remembered device silhouette, or the current vertical coordinate of a pin.

## Compose TOP In Two Dimensions

1. Build full visual BBoxes for all hierarchical modules before assigning TOP coordinates. A symbol-body BBox alone is not a collision envelope.
2. Place modules by signal flow, functional role, and power domain, using both horizontal and vertical free space. Reserve short routing and label channels between related blocks.
3. Keep the composition compact but not crowded. Do not compress every module into one vertical column, leave large unused quadrants while another area is congested, or let names, pin banks, supply stubs, labels, and frames invade neighboring envelopes.
4. Keep directly related modules close enough for a short local connection. Use named-net stubs for nonlocal cross-block connections instead of page-scale fly wires.
5. Recompute the TOP canvas and route channels after symbol or pin-bank dimensions change. Fixed coordinate increments and body-only spacing are rejection conditions.
6. After an authorized removal of obsolete ports, ignored instances, or a disabled island, rebuild the composition from the surviving active envelopes. Compact affected pin banks without ghost slots, delete only the now-orphaned owned frame or annotation objects, and do not preserve a blank band or old canvas extent as a historical placeholder.

Compactness is measured against the complete visible content, not the symbol count or raw canvas area.

## Use Native Scalar And Bus Semantics

- Draw every scalar signal, including one-hot controls and scalar supplies, with the project's ordinary thin schematic wire style.
- Use a thick line or bus representation only for a real multi-bit bus whose electrical interface has matching bus semantics.
- Never merge independent scalar controls into a visual bus or use a wide generic path merely to simplify generation.
- Preserve the same-project wire LPP, width, label style, and junction convention, and bind every visible electrical segment to its intended real OA net.

## Separate Local Wiring From Cross-Block Naming

- Inside one functional island, express the relationship with short continuous netted wires and real junctions. Do not hide a nearby series, parallel, mirror, clamp, or switch relationship behind repeated labels.
- Across functional blocks or hierarchy regions, terminate each endpoint in a short netted stub and place the real net name on that stub. Both stubs must read back on the same actual OA net with the same exact name; equal label text alone is not proof.
- Derive generated label text from the connected OA net after binding. Never invent it from a planned role, symbol text, screenshot, index, or coordinate.
- Do not use long wires to compensate for poor placement. A cross-block label shortens presentation; it does not create connectivity or authorize a net rename.

## Make Every Supply Connection Visible And Electrical

Every supply, ground, body, well, and intermediate-rail terminal in scope must have a clear visible rail or short stub that is bound to its real OA net.

- A hidden `instTerm` binding, nearby text, decorative line, or global-looking name does not satisfy this rule.
- Scalar supply rails use the project's ordinary thin schematic wire unless the approved project exemplar has a distinct native electrical rail convention that is not bus semantics.
- Keep separate voltage domains visually distinct. Never let shared placement or a frame imply that two rails are shorted.
- If the ordinary stub generator deliberately excludes power nets, the same generation plan must invoke a separate supply-rail or supply-stub generator. It must cover every excluded power terminal and bind each segment to the actual supply net.
- Reject a generation result when any power terminal is absent from both the ordinary-stub coverage set and the replacement-supply coverage set.

A useful coverage record is:

`instance | power terminal | real net | visible rail/stub object | generator | readback result`

## Build Pin Banks As Boundary Objects

- Assign every schematic terminal to a named bank or a justified exception before moving any pin.
- All members of one same-direction bank share one boundary coordinate: one `x` for a vertical bank or one `y` for a horizontal bank.
- Within a signal functional group, use the fixed preferred center pitch `0.125` schematic units. Signal groups may have a deliberate larger separator, but that separator does not change the `0.125` pitch inside either group. Top power and ground groups follow the separate compact-group rule below.
- Put the pin figure outside the cell boundary and the terminal name inside. Keep every signal terminal name horizontal and visible; this terminal-name rule takes precedence over generic advice that permits rotating ordinary net labels. A top power-pin name may retain the selected exemplar's existing direction.
- Move the pin figure and its owned terminal-name display as one visual unit. Preserve terminal identity, exact name and case, direction, net, and hierarchy consumers.
- Resolve signal-bank text pressure by horizontal name placement, bank order, symbol width, or an explicit group gap. Do not silently alter the signal within-group pitch, hide a signal name, rotate a signal terminal name, or leave it overlapping the body, border, another pin, or instance text. Resolve top power-group text pressure under the exemplar-derived spacing and name-direction rule below.
- Preserve functional grouping through bank order and explicit group gaps, not by stretching individual pins to match distant internal block coordinates.

The order of pins in a bank is a visual choice after electrical identity is known. It is never the key used to connect the hierarchy.

## Symbol Write Authorization Gate

Treat `schematic` and `symbol` as independent write domains. None of the following authorizes a symbol mutation:

- permission to edit a schematic or move schematic pins;
- permission to clean or migrate an interface;
- permission to update parent connections or make hierarchy views consistent;
- a generator's ability or preference to synchronize or rebuild a symbol;
- the user's own prior or current manual symbol edit.

Before opening a symbol appendable, obtain current-task confirmation that binds all of these fields:

`library | cell | view=symbol | terminal additions/deletions/direction changes | pin banks and order | body dimensions | title and text treatment | expected parent impact`

The user may authorize only a subset, such as geometry without terminal changes. Freeze that subset as the symbol write domain and leave every unlisted property unchanged. Parent-instance, parent-symbol, testbench, or configuration updates remain separate write domains and require their own confirmation.

If a read-only comparison finds a schematic/symbol mismatch but the symbol gate has not passed, report the exact name, direction, bank, body, or text difference and stop. Do not treat `cross-view` failure, interface cleanup, or an "auto-generate matching symbol" helper as emergency permission to write the symbol.

## Apply The Approved Hierarchical Symbol Grammar

- Apply this section only after the symbol write authorization gate passes. During a read-only review, use it to report required corrections without mutating the symbol.
- Derive the symbol width from measured text and pin-bank bounds. Choose the smallest on-grid body width that gives the left and right pin names, the centered green title, and their required clearances no overlap. Reject both text collision and a wider mostly empty body; an exemplar supplies proportions and relationships, not an absolute width.
- For every left, right, and top red pin figure, place its center/electrical access point exactly on the corresponding green body-border segment. Construct the body border through those access coordinates; do not use a body inset that leaves a pin center floating inside or outside the border.
- Keep each same-direction signal group at `0.125` center pitch. In the approved rendered style, the red pin name stays inside the body and the blue external net name stays outside at the outward end of its real-netted stub. Derive the external label from the actual OA net; color and position do not create connectivity.
- Put all power and ground pins in compact groups on the top border. Take their spacing from the selected same-project exemplar or from an explicit compact-group rule based on text bounds and clearance. Never distribute them uniformly across the full symbol width merely because space is available. Their access centers still lie exactly on the top body border, and their pin names may use the exemplar's established top-pin direction.
- Preserve object roles even when display resources change: body border and centered title are body graphics, red pin names belong to terminals, and blue names belong to external real nets. Do not hard-code display colors or LPPs as electrical semantics.

These constraints are portable geometric relationships. The named exemplar remains a case study, not a mandatory cross-process cell or fixed-size template.

## Synchronize Hierarchical Interfaces By Name And Role

For every hierarchical port, verify one record keyed by exact terminal name and electrical role:

`name | role/direction | child schematic terminal | child symbol pin | parent instTerm | parent real net`

- The schematic terminal, symbol pin, and parent instance terminal must agree in exact name and intended role. Preserve case where the project treats names as case-sensitive.
- The parent `instTerm` must bind to the intended real OA net for that named role.
- Compare interface sets and keyed mappings, not only counts.
- Never connect or synchronize ports by array index, enumeration order, sorted `y` coordinate, nearest pin, or producer/consumer display order.
- If a name or role is absent, duplicated, or ambiguous, stop. Do not guess a positional correspondence.
- A symbol-pin reorder for readability may change geometry only; it must not change the name-keyed hierarchy mapping.

Producer and consumer interfaces keep their own verified roles. Do not propagate a consumer's port direction or pin graphic backward into the producer merely because both sides share a net. In the approved level-shifter grammar, `G_P_DRV`, `G_N_DRV`, and the other confirmed members of their output group retain terminal direction `output` and the output-pin (`opin`) graphical form at the producer. A consuming analog boundary may independently remain `inputOutput` when its own interface contract requires that role.

## Use Compact Level-Shifter And Digital-Cell Templates

- For `LEVEL_SHIFTER`, enumerate the exact `VSS1`, `VDD1`, `VSS2`, and `VDD2` instance terminals and read each terminal's real OA net before drawing. Do not infer a mapping from suffixes, array order, coordinates, or a previous process.
- Give those four supplies four one-to-one short stubs or connections in a compact group. Keep them uncrossed and visually unambiguous; place each real net label on or immediately beside its own stub. A shared-looking label cluster, crossing, or detached label is a rejection condition.
- For a digital cell whose verified master exposes input `A` and output `Q`, route `A` horizontally out to the left and `Q` horizontally out to the right from their transformed access points. Put each real net name at the outer end of its line, not in a pile under the device.
- Keep the digital instance name, master name, and supply names visible with nonzero clearance from symbols, wires, and net labels. The A/Q template controls drawing only; actual master-terminal identities and nets still come from OA.

## Draw Transmission Gates With One Standard Grammar

Apply this grammar only after confirming that the devices form a real complementary transmission gate and reading the actual master terminal mappings.

1. Place the PMOS above and the NMOS below as one compact functional island.
2. Orient them from their transformed master pins so the two real conduction endpoint nets form a short parallel rectangular path. The data or analog signal reads horizontally from left to right through the pair.
3. Join the PMOS and NMOS terminals belonging to the left endpoint with one short netted side, and do the same for the right endpoint. Determine which physical pins are `D` or `S` from the actual master mapping; never guess or swap them for symmetry.
4. Bring the complementary gate controls vertically, with the PMOS control presented above and the NMOS control below. Each gate stub and label must bind to its real control net.
5. Give body and supply terminals clear real-netted rail or stub treatment under the supply-coverage rule.
6. Keep the rectangle short enough to read as one parallel switch, while preserving symbol, name, parameter, pin, and wire clearance.

Reject a TG that is represented as two distant devices joined only by labels, has crossed or diagonal control wiring without need, uses guessed D/S/G/B identities, or changes the electrical endpoint pairing to obtain a cleaner rectangle.

A request to repair one local TG authorizes only that TG and its explicitly named local wiring. It does not authorize clearing, regenerating, or rearranging the enclosing analog schematic.

## Protect User-Confirmed Exemplars And Use Frames Correctly

A user-marked red review box, an existing white frame, or another explicit approval marker identifies a protected exemplar region. The review color itself is not a portable layer or electrical convention.

- Freeze the exemplar's instances, transforms, terminal mappings, local netted routes, junctions, labels, and complete visual bounds before adjacent work.
- Do not move, rotate, reconnect, redraw, or crowd a protected object without a new explicit authorization.
- Treat user-approved current mirrors, fast and slow branches, protection branches, and their local routes as protected exemplars. A local TG request does not weaken that protection.
- Extract only portable grammar such as compact grouping, short local trunks, branch visibility, and text clearance. Do not copy incidental process symbols, absolute coordinates, or display colors.
- A functional frame is a non-electrical annotation. Create it on the project's approved drawing or annotation LPP with no net, terminal, or pin meaning.
- Fit the frame tightly around the final visible contents with uniform clearance. It must not cover devices, wires, names, parameters, pins, labels, or adjacent frames.
- Keep the unframed circuit readable. A frame cannot justify scattered devices, hidden topology, excess whitespace, or crowding.

If a failed edit disturbed protected or out-of-scope content, roll back first. Restore the narrowest authoritative unit that fully covers the damage: the affected region when the baseline supports an exact regional restore, or the affected view when the transaction contaminated the view. Re-read both baselines after restoration, then patch only the explicitly authorized TG and local wires. Record the rollback and the subsequent patch as separate geometry diffs, and maintain an independent electrical diff throughout; a clean-looking restore is not electrical proof.

## Keep Analog Functions Traceable

- Form compact analog functional islands around actual local relationships: current mirrors, diode-connected references, differential pairs, clamps, protection stacks, bias branches, and switch paths.
- Show a mirror reference device's real `D=G` relationship as one explicit continuous T-shaped route: reference drain to common gate trunk, with real branches to replicated gates.
- Keep directly related series and parallel paths visible with short continuous wiring. Use cross-island labels only after the local topology is readable.
- Require every visible electrical `line`, `path`, and `pathSeg` to read back on its intended real OA net. A visually touching object with `net=nil` is an error.
- Cosmetic frames, notes, and junction markers remain non-electrical and must not be used to disguise missing netted geometry.

## Preserve Topology And Report Two Diffs

Readability work must leave the approved electrical contract unchanged. Verify and report two independent normalized comparisons:

1. **Electrical diff:** masters, parameters, schematic terminals, symbol pins, parent instance terminals, terminal-to-net tuples, ports, and nets.
2. **Geometry diff:** instance origins and orientations, pin and name placement, symbol bounds, wires, stubs, labels, junctions, frames, annotations, and full visual BBoxes.

A valid readability-only result has no unexplained electrical difference and may have intended geometry differences. Never describe a geometry-only change as a topology change, or use a clean visual diff to claim electrical equivalence without the electrical comparison.

## Acceptance Gate

Reject the result if any of these conditions remains:

- TOP modules are compressed into one crowded column, overlap under full visual BBoxes, waste usable two-dimensional space, or depend on large fly wires;
- a symbol was opened for write or changed without a current exact symbol authorization, or a schematic/interface/parent operation was used as implicit symbol permission;
- a scalar uses bus/thick geometry, or a real bus is decomposed without an interface reason;
- a local functional relationship is hidden behind labels, or cross-block same-name stubs are not bound to the same real OA net;
- any power terminal lacks a real-netted visible rail/stub, including power terminals skipped by the ordinary stub generator;
- a same-direction signal bank lacks one shared boundary coordinate, `0.125` within-group pitch, red inside pin names, blue outside real-net names, or pin/name unit movement;
- a symbol ignores the same-project approved exemplar, lacks its required identifying title, is not the smallest on-grid width that clears its pin names and centered title, contains a giant empty body, has a left/right/top access center off the body border, uses an inset border, or overlaps its body, pins, names, or instance text;
- power or ground pins are not grouped compactly on top, are averaged across the full width, or violate the approved top-name direction and clearance;
- any hierarchy connection was paired by index, order, or coordinate instead of exact name and role;
- a producer's `G_P_DRV`, `G_N_DRV`, or peer output lost its `output`/`opin` form because a consumer is `inputOutput`;
- a `LEVEL_SHIFTER` supply mapping was not derived from the real OA nets, or its four `VSS1`/`VDD1`/`VSS2`/`VDD2` connections are not one-to-one, short, compact, uncrossed, and labeled at their own stubs;
- an A/Q digital cell lacks a left-horizontal `A` exit, right-horizontal `Q` exit, endpoint net labels, or clear instance, master, and supply names;
- a TG violates the PMOS-above/NMOS-below, horizontal parallel endpoint, vertical complementary-gate grammar or relies on guessed terminal identities;
- a local TG request cleared or rearranged protected analog content, rollback was not limited to the affected region or view without evidence, or the repair lacks separate electrical and geometry diffs;
- a protected exemplar changed or a functional frame acquired electrical meaning, became oversized, or obscured content;
- an analog island is scattered, a mirror `D=G` T-route is hidden, or a visible electrical line/path/pathSeg has no real OA net;
- an authorized removal left deleted-terminal ghost slots, a disabled-island hole, an empty legacy frame, or stale canvas extent instead of recomputing the active composition;
- electrical and geometry differences were not checked and reported separately.

Passing this gate establishes only schematic readability and electrical traceability. It does not prove circuit function, simulation correctness, PVT, SOA, DRC, LVS, reliability, or signoff.
