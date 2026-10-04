# Compact Functional-Block Schematic Style

Use this guide when a user marks part of an existing schematic as the correct drawing style or when a generated analog block is electrically connected but visually scattered. It governs visible organization only; the current netlist and OA instance-terminal mappings remain the electrical authority.

## What The Approved Example Demonstrates

The reusable pattern is a compact functional island with locally explicit topology:

- A small parallel switch or clamp pair shares its two endpoint nets through short, symmetric local wiring. The two devices are visually grouped as one function rather than separated and reconnected only by labels.
- A reference device, controlled fast and slow branches, and an output protection device are placed close enough that the shared rail, mirror-control net, intermediate node, and output path can be followed directly.
- A genuinely shared local net uses one short trunk with visible branch points. Series devices form a readable stack. Parallel branches occupy neighboring tracks.
- Device orientation makes transformed pin exits face the intended local connection where possible. This reduces bends without changing terminal identity.
- The block consumes only the area required for symbol clearance, labels, junctions, and routing. Empty rows or columns are not inserted without a routing or hierarchy reason.

These are visual rules, not claims that the example circuit is functionally correct, reliable, or suitable for another process.

## Protected-Example Contract

Before editing near a user-approved example, record:

`object | identity | geometry/orientation | electrical mapping | protected scope`

The protected scope should include, as applicable:

- instances and master cells;
- instance origins, orientations, and transforms;
- each master terminal to actual net mapping;
- local wires, path segments, junctions, and wire endpoints;
- labels and annotations that are part of the approved presentation;
- the functional-island bounds needed to prevent overlap from adjacent edits.

Do not move, rotate, mirror, reconnect, delete, relabel, or redraw protected objects unless the user explicitly changes the scope. Moving an adjacent block into the protected bounds also violates the contract.

## Full Visual Bounds And Hierarchical Symbols

- Compute a full visual BBox before placement. Union the master or symbol body, transformed pin access points and figures, pin names, instance name and property text, power pins, and all owned connection stubs; then add deliberate on-grid clearance. A master body BBox alone is not a placement envelope.
- At TOP level, place hierarchical modules from their complete visual envelopes and signal-flow roles. Do not use a fixed-coordinate increment that creates a mechanically continuous stack. No module body, pin bank, pin name, instance name, power pin, or stub may enter another module's visual envelope.
- Inside a standard-cell or level-shifter schematic, compute spacing from each master's full visual BBox and pin/text extent. Align cells in one functional domain, then leave visibly larger gaps between different domains. The `0.125` schematic-unit rule is exclusively for compact same-direction external pin banks; it is never an internal-cell or hierarchical-module pitch.
- Use a user-approved symbol from the same project as the real geometry and style exemplar for every new symbol. Derive border style, text style, pin figure/access convention, nominal density, and role ordering from that exemplar. Do not synthesize a large empty rectangle merely from the port count.
- Size a symbol tightly enough to avoid meaningless whitespace but large enough to contain all pin banks and text with clearance. Group left and right pins in functional order, and make producer output order correspond to consumer input order where the interface is paired. Inputs-left, outputs-right, supplies-top, and grounds-bottom are common project patterns, not universal geometry.
- Place each electrical pin access point exactly on the symbol boundary, the pin figure outside the body, and the pin name inside. Reject any overlap among a pin figure, name, border, instance text, or adjacent symbol.

## Placement Grammar

1. Identify local circuit relationships before choosing coordinates: shared rails, mirror gates, source or drain stacks, switch branches, protection paths, and output nodes.
2. Build one compact island per tightly coupled function. Keep unrelated functions outside that island even when extra packing would reduce the total canvas.
3. Align equal-role devices on a common row or column. Align series devices along the direction of current or signal flow. Place parallel alternatives on adjacent tracks.
4. Place reference and replicated devices near their shared control net. Put a local switch beside or immediately in series with the branch it controls.
5. Place protection or level-limiting devices next to the node they protect, with the protected-node path visible.
6. Use the nearest on-grid spacing that preserves each object's full visual BBox, wire, and label clearance. Keep repeated device and branch gaps consistent. The universal `0.125` center pitch applies only to compact same-direction external schematic pin banks and must not be used for internal devices, standard cells, level shifters, or hierarchical modules.
7. Compress the block as a unit only after connectivity is routed. Stop compression before any object collision, ambiguous branch, or wire-through-symbol condition appears.

## External Interface Bank Grammar

- Inventory the complete cell interface before moving pins. Assign every terminal to a boundary bank or record why it must remain outside the bank plan. When the requested scope is all IO, partial cleanup of one bank is not completion.
- Treat external pins as a boundary bank, not as leftover objects tied to an earlier internal-device location. Recompute their placement after functional islands move.
- Select the side by interface role and signal flow. When a user-approved right-edge example applies, align the pin figures in one vertical column, place names immediately to their left, and point the pin access toward the cell interior. Use analogous row or column grammar on other sides.
- Derive the bank side and offset from signal flow and adjacent functional-block bounds, but use the cross-process default center pitch `0.125` schematic units for every compact same-direction pin bank. On a `0.0625` schematic grid this equals two grid steps. Do not scale this pitch with PDK, process node, internal device size, or canvas size.
- Keep pins compact and ordered. All members of one row or column bank use one common boundary coordinate and `0.125` pitch. Do not spread a bank to align each pin with a distant internal functional band; preserve that association through pin order and naming. If labels collide, reposition or reorient the text first. Do not increase pitch without reporting the conflict and obtaining explicit direction. A pin should not occupy a distant empty region merely because an old generator assigned it a fixed coordinate.
- Prefer named-net connectivity between a boundary pin and a distant internal block over a long decorative fly wire. The terminal, pin, and internal branch must still share the same real OA net.
- Moving a schematic pin for readability must preserve its terminal name, direction, pin identity, net, and hierarchy contract. The symbol view and parent instances are separate scopes and remain unchanged unless explicitly authorized.
- Move the pin figure and its terminal-name display together. Orient the name toward the circuit and preserve clearance from neighboring pin labels, devices, property text, and wires.
- Report every bank, its member list, common boundary coordinate, pitch, and exceptions. Do not infer whole-cell completion from one compact bank while other pin groups remain widely scattered.

## Functional Frames And Notes

- Use a visible rectangular frame to communicate one coherent functional island when grouping is not already obvious from proximity and local wiring. The frame is a review aid, not an electrical object.
- Compute the frame only after placement, routing, names, parameters, pin text, and local labels have reached their intended locations. Its interior bounds must include all owned visible objects plus uniform on-grid clearance.
- Place one concise note immediately outside a consistent frame edge. Prefer a literal block name or circuit role over a sentence. Align notes across peer blocks when practical.
- Use the current project's established non-electrical frame and annotation LPPs. Do not encode white, orange, or any other display color as electrical or cross-process semantics.
- Keep the framed island compact: eliminate avoidable blank rows, columns, and route detours before framing. Preserve enough clearance that symbols, device properties, terminal names, net labels, junctions, and wires remain independently legible.
- Reject frames that cut through electrical objects, overlap another frame, contain unrelated circuitry, omit an owned branch, or leave so much whitespace that the visual grouping becomes weak. Reject notes that obscure wiring, float far from the frame, or attempt to explain an unreadable internal circuit.

## Local Wiring Grammar

- Route shared local rails and control nets first as short orthogonal trunks.
- End every branch at a real terminal or junction. Do not rely on visual crossings or nearly coincident endpoints.
- Prefer one continuous local wire over multiple same-name stubs inside the same visible island.
- For a current mirror, show the diode-connected reference device explicitly: connect its drain to the common gate trunk and connect each replicated gate to that same continuous route. Place the T-junction at the actual branch point instead of expressing the relationship through separated duplicate labels.
- Require every visible electrical line, path, or path segment to read back on the intended OA net. Reject a visually connected `net=nil` route; allow a netless dot or ellipse only as a cosmetic marker placed exactly on a verified electrical junction.
- Use labels for cross-block, hierarchical, or intentionally global nets. A label must not conceal the internal structure of a mirror, stack, switch pair, bias branch, or protection path.
- Avoid loops and detours that add no topological information. A rectangular route is useful only when it clearly joins parallel endpoint nets while preserving device and text clearance.
- Keep labels on or close to their real wire endpoints and outside the dense center of the functional island. Match label rotation to the local route when useful, and remove label-only wire extensions that add no connectivity or clearance benefit.

## Native Scalar, Bus, And Path Style

- Inspect a user-approved schematic in the same project before drawing. Reuse its ordinary wire LPP, scalar line width, true-bus representation, label LPP, font, height, orientation, and offset conventions; do not invent a visually separate generator style.
- Draw every scalar net with the project's ordinary thin schematic wire. A thick line or bus is valid only for a real multi-bit bus with corresponding electrical semantics. Eight independent one-hot nets such as `STATE0` through `STATE7` are eight scalar wires, not one bus.
- Do not use a physically wide `dbCreatePath` uniformly at every terminal merely because it is convenient for background generation. Select the project's native wire object or established path form and width for that net class, then bind every visible electrical segment to the intended OA net.
- Preserve label style together with wire style. A visually correct scalar stub still fails if its line width, LPP, label geometry, or OA net binding differs from the accepted project convention without an explicit reason.

## Analog Functional-Island Grammar

Analog readability is a hard acceptance gate, not optional decoration. Do not clear an existing readable analog drawing and mechanically fan every MOS terminal into disconnected-looking stubs.

For a segmented mixed-signal driver that contains these roles, make all eight islands explicit and spatially distinct:

- `strong VCM` and `weak VCM`;
- `P fast`, `P slow mirror`, and `P three-level protection`;
- `N fast`, `N slow mirror`, and `N three-level protection`.

Within and between those islands:

- Keep each current-mirror reference device's `D=G` connection and common gate trunk continuous, visibly T-branched, and bound to the real OA net. A visible wire/path/pathSeg with `net=nil` is an error even when it appears to touch the right terminals.
- Make the fast and slow branches, `PX`/`VO`/`NX` path, parallel protection devices, and `VDD15` intermediate-level injection directly traceable. Use short continuous thin wires inside an island and labels only across islands or for genuinely global nets.
- Group internal standard cells and level shifters by functional domain. Align peers inside one group and use larger gaps between groups so bodies, pins, names, and power terminals cannot collide.
- A non-electrical frame and short note may identify an island, but the unframed circuit must already be readable. A frame cannot justify scattered placement, hidden branch relationships, or excess blank space.
- During interface migration or digital-cell deletion, treat the user's approved old geometry or backup as the protected analog exemplar. Preserve correct MOS placement, mirror T-routes, device orientation, and local branch relationships; modify only the authorized interface and obsolete digital objects instead of clearing and redrawing the analog shapes.

## Orientation And Terminal Safety

Choose rotation or mirroring from transformed master-pin geometry and local routing needs. The objective is to make the correct pins face their wires, not to make a familiar transistor silhouette.

Never improve appearance by exchanging D/S/G/B or any other terminals. After placement and routing, compare every `(instance, master terminal, net)` tuple against the approved contract or baseline. A visually cleaner drawing with an unexplained terminal change is a failed result.

## Reject These Patterns

- Members of one current mirror or bias branch scattered across the page.
- TOP-level hierarchical modules stacked at a fixed increment even though their full visual bounds overlap.
- Internal standard cells or level shifters spaced at `0.125` as though they were an external pin bank, or packed so bodies, pins, names, and power terminals touch.
- A generated symbol whose port-count-driven empty body ignores the project's approved symbol exemplar, or whose access point, pin figure, pin name, and border overlap.
- A scalar net drawn with a bus or thick path, including independent one-hot state nets presented as one bus.
- Uniform physically wide `dbCreatePath` stubs on all terminals without discovering the project's native scalar wire and label style.
- A local topology represented mainly by repeated net names when short direct wiring is practical.
- Long wires used only to compensate for poor placement.
- Large blank gaps between directly related devices.
- Inconsistent pitch or orientation among repeated branches without a circuit reason.
- Junctions implied by crossings, collinear overlaps, or endpoints that do not actually coincide.
- A local mirror whose reference drain and shared gates are represented only by repeated labels despite room for one direct route.
- A visible electrical wire or path that reads back with no OA net.
- External pins left at obsolete internal-device coordinates, scattered through empty canvas, or arranged with inconsistent boundary alignment and label direction.
- Pins described as one IO bank but distributed at internal-block heights with large nonuniform gaps.
- A same-direction compact pin bank using a center pitch other than `0.125` without an explicitly reported and approved exception.
- Declaring all IO compact after editing only one bank while other terminal groups retain obsolete or widely spaced coordinates.
- Oversized or overlapping functional frames, frames cutting through owned objects, notes detached from their frames, or framed blocks whose internal names, parameters, labels, pins, and wires overlap.
- A pin relocation that recreates or renames the terminal, changes its direction or net, or silently alters the symbol/parent interface.
- Decorative compression that overlaps symbols, properties, pins, labels, or wires.
- Clearing readable analog shapes and replacing every MOS terminal with isolated mechanical stubs.
- A segmented driver whose VCM, fast, slow-mirror, or three-level protection roles cannot be identified as distinct islands, or whose `PX`/`VO`/`NX`, parallel protection, or `VDD15` path cannot be followed directly.
- Reformatting a user-approved protected region without explicit authorization.

## Review Evidence

For each functional island, report:

- included instances and local nets;
- whether shared, series, and parallel relationships are visibly explicit;
- whether placement and gaps are compact and consistent on the active grid;
- whether TOP modules and internal cells clear one another under full visual BBoxes rather than body-only BBoxes;
- whether new symbols follow a same-project approved exemplar, contain pin banks and text without excess whitespace, and preserve functional pin order;
- whether scalar wires use the established thin style, true buses alone use bus/thick style, and one-hot nets remain separate scalars;
- whether labels are limited to appropriate cross-block or global use;
- whether current-mirror drain/gate relationships and branch junctions are visibly continuous;
- whether every visible electrical route has the intended OA net binding;
- whether external pins form deliberate boundary banks with consistent alignment, inward-facing labels, and preserved terminal contracts;
- whether the terminal inventory is complete and every pin belongs to a reviewed bank or explicit exception;
- whether functional frames tightly and unambiguously contain their owned circuitry, notes identify the correct block, and framed contents remain compact without crowding;
- where applicable, whether all eight segmented-driver analog islands and the fast/slow, `PX`/`VO`/`NX`, protection, and `VDD15` paths are directly traceable;
- whether protected exemplar objects remained unchanged;
- whether terminal-to-net tuples match the authoritative baseline.

Readability approval does not prove simulation behavior, PVT coverage, SOA, DRC, LVS, reliability, or signoff.
