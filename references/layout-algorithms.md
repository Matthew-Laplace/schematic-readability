# Placement And Routing Algorithms For Readability

This file holds the algorithmic layer: how to *compute* a readable placement
when hand-picking coordinates is not enough. It exists because the rest of this
Skill says what a readable schematic looks like, not how to search for one.

Everything here is `[reported]` from a 2026-10-04 survey unless marked
otherwise - the algorithms were read by a parallel survey pass, not line by
line by the author of this file. **Treat the weights and constants as a
starting point to re-derive, not as validated defaults.** Before adopting any
constant, verify it against the source and re-scale it to the project grid.

## When To Use This Layer

Use it only when placement is genuinely under-determined. For a schematic that
already has a confirmed layout grammar, or where the user marked an exemplar,
the rules in `compact-functional-block-style.md` and the placement gates in
`SKILL.md` take precedence. An algorithm that "improves" a protected exemplar
is a defect regardless of its objective function.

## 1. Constraint-Weighted Iteration

The most directly transferable model: score the placement, try a move, keep it
only if the score improves, stop on a plateau.

```
score = SUM_over_constraints( weight(c) * satisfied_fraction(c) )

loop:
  for c in constraints:            # round-robin, not nested
      apply c
      repair_routes()
      rebuild_spatial_bins()
  if score - best_score > epsilon: best_score = score
  else: stall += 1
  if stall >= stall_limit: return history[best_index]   # roll back to peak
```

### Observed Configuration

| Item | Value | Note |
|---|---|---|
| Constraint weights | avoid-components `100` > avoid-lines / avoid-bboxes `20` > left-to-right / input-align / untangle `10` > vertical-sort `0` | The ordering matters more than the numbers: never trade a collision for a crossing |
| Improvement epsilon | `0.1` | |
| Stall limit | `10` rounds with no new peak | |
| Spatial bin size | `100` units | |
| Route repair | after every constraint round | |

The **weight ordering encodes the priority policy**, and that policy is
reusable even if the numbers are not: hard geometry first, then congestion,
then signal-flow aesthetics. Vertical sort has weight `0`, i.e. it is only a
tie-breaker, which is the honest way to express "prefer centred, but never at
the cost of anything above".

### Early-Stop Discipline

The loop tracks the **peak** score and returns the configuration at the peak,
not the last one. That detail prevents the classic failure where the final
iteration happens to be worse than an earlier one. Any home-grown optimiser
should carry the same rollback-to-best behaviour, and must have a bounded
iteration count - never an open-ended "until it looks good".

## 2. Layered Placement By Signal Flow

Left-to-right flow can be computed rather than eyeballed, by treating the
netlist as a DAG and assigning each device a column equal to its longest path
from an input.

```
adjacency A: A[source][target] = +1, A[target][source] = -1

depth(i):
    if i has no predecessor: return 0
    if i is on a cycle:      return -1        # feedback, placed specially
    return 1 + max(depth(j) for j where A[i][j] == -1)

x(i) = x0 + depth(i) * column_gap
```

Feedforward stages land in successive columns by construction; feedback paths
return `-1` and are routed around the perimeter rather than being allowed to
pull a device backwards.

**Why this matters for analog work.** A current mirror, a cascode stack, and a
differential pair are rarely a clean DAG, so blind longest-path layering will
flatten a legitimate symmetric group into arbitrary columns. Apply layering per
**functional island** and keep symmetry constraints at a higher priority than
column assignment.

## 3. Vertical Ordering By Barycentre

```
y(i) = mean( y(j) for j in predecessors(i) )
score = -SUM( abs( y(i) - y(i)_target ) )
```

This is the classic crossing-reduction heuristic for a layered graph. Use it
only as a tie-breaker, and re-snap to the grid afterwards - the mean of grid
values is generally not on the grid.

## 4. Crossing Minimisation By Pin Mirroring

Cheaper and more targeted than moving devices: when two wires cross, swap the
*pin order* on one endpoint if the symbol permits it.

```
for (a, b) in candidate_pairs_near_each_other():
    if not segments_cross(a, b): continue
    if a.end_entity != b.end_entity: continue      # only same-endpoint pairs
    before = count_local_crossings()
    swap_pins_up_down(a.end_entity)
    after = count_local_crossings()
    if after >= before: revert()                   # greedy, monotone
```

Two implementation notes worth keeping:

- **Candidate pruning matters.** Testing every pair is quadratic; bucket
  segments into spatial bins and only test pairs inside a bin and its
  neighbours. The survey's implementation checked the own bin plus four
  neighbours.
- **Crossing test degenerates.** A general "do these segments straddle each
  other" test must special-case collinear segments, where it degenerates to a
  bounding-box intersection.

Pin mirroring **must not** be confused with terminal swapping. Swapping which
pin a wire reaches is a connectivity change and is forbidden by Save Gate 1.
Mirroring the symbol while keeping the terminal-to-net map identical is a
geometry-only change. This distinction is the whole reason the technique is
safe.

## 5. Route Straightening And Obstacle Avoidance

### Manhattan reduction

Realise each route as at most four points, taking the x break at the midpoint
of the two endpoints' x values. When the two points share an x or a y, collapse
to a single straight segment. This removes the "go left, then down, then right"
class of detour that reads as a mistake.

### Bounding-box detour

```
if segment intersects the bbox of any non-endpoint component:
    route = [start,
             (b.x_min - ext, y_start),
             (b.x_min - ext, y_bypass),
             (b.x_max + ext, y_bypass),
             (b.x_max + ext, y_end),
             end]
    choose y_bypass above or below by comparing the segment's mean y to the
    obstacle's centre y
```

An extension margin prevents the route from grazing the symbol edge. The
corresponding prohibition is already in `SKILL.md`: a wire must not pass
through a symbol body.

### Parallel-run separation

Two collinear or parallel same-direction segments whose bounding boxes overlap,
excluding head-to-head and tail-to-tail cases, are separated by offsetting the
inner one by a minimum line spacing. This is what keeps a bundle of
almost-overlapping rails from reading as a single thick line.

## 6. Routing As A Costed Search

A more capable model, observed in an older C implementation, scores candidate
routes rather than repairing them:

```
cost = (used_tracks / available_tracks) * TRACK_WEIGHT
     + congestion / available_tracks
     + corners * CORNER_COST
     + length * LENGTH_WEIGHT

if used_tracks >= available_tracks - 1:      # near saturation
    cost = 5 * cost + 40
```

Observed constants: `TRACK_WEIGHT 30`, `LENGTH_WEIGHT 1`, `CORNER_COST 4`.
The **near-saturation blow-up** is the interesting part: it makes the router
prefer a longer detour over consuming the last free track, which is what keeps
congested regions readable. Routes are refined by rip-up-and-reroute.

Scaling note: this implementation works in a corner-stitched tile space. Porting
it to OA means constructing an equivalent occupancy grid first; there is no
direct mapping to OA objects.

## 7. What Is Portable To OA

| Technique | Portable | Note |
|---|---|---|
| Constraint-weighted loop with early stop and rollback-to-peak | **Yes** | Ordinary Python; no tool dependency |
| Hard/soft constraint tiers with structured diagnostics | **Yes** | Model already described in `readability-rules.md` section 6 |
| Longest-path layering | **Yes** | Operate per functional island, not globally |
| Barycentre vertical ordering | **Yes** | Re-snap to the project grid afterwards |
| Pin-mirror crossing reduction | **Yes** | Requires reliable transformed pin geometry, which `SKILL.md` already demands |
| Manhattan reduction and bbox detour | **Yes** | Pure geometry over the transformed bounds you already compute |
| Spatial binning for pairwise tests | **Yes** | Needed at any realistic instance count |
| Costed routing with rip-up-and-reroute | **Partly** | Requires building an occupancy model; OA has no track concept |
| Corner-stitched tile routing | **No** | Depends on a tile data structure with no OA equivalent |

## 8. External Layout Engines

Two general graph-layout engines appeared repeatedly in the survey and are
worth knowing about, with the same caveat: neither understands analog
structure.

| Engine | Relevant capability | Limitation for analog |
|---|---|---|
| ELK / elkjs | Layered crossing minimisation, orthogonal edge routing, port-side constraints; exposes bend points and aspect ratio as readable outputs | Device-agnostic; needs a MOS symbol skin built from scratch. Its notion of "node" is a box, not a transistor |
| netlistsvg | Skins over a layout engine; ships an analog skin with opamp, BJT, diode, R, L, C, transformer, ground, VCC | The shipped analog skin has **no MOSFET symbol**, and only one module is rendered per invocation |

If an engine is used at all, use it to produce a **candidate** geometry, then
pass that candidate through this Skill's gates unchanged. An engine's own
"layout quality" output is not evidence of connectivity preservation.

## 9. Known Upstream Defects

Recorded so they are not mistaken for reference behaviour:

- The surveyed Python constraint solver's `main()` unpacks three values from a
  function returning two, so its CLI entry point raises.
- That same project computes an EESchema-specific spacing table and never
  passes it into the solver, so those constants are dead code.
- Its published per-constraint weights are hand-tuned and the project documents
  no definition of a "good schematic"; the loop maximises its own weighted sum
  and stops on a plateau.

Conclusion: adopt the **structure** of these algorithms. Do not adopt their
constants, and do not assume an upstream optimiser's output is readable just
because its objective converged.
