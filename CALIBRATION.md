# Calibrating This Skill For Your Project

[English](CALIBRATION.md) | [日本語](CALIBRATION.ja.md) | [繁體中文](CALIBRATION.zh-TW.md)

## What "Local Calibration" Means Here

This is **not** model fine-tuning and it does not change any AI weights. It is a
prompt-and-configuration exercise: several values in this skill are marked
`[calibrated]` precisely because they are starting points, not facts. Local
calibration means replacing those defaults with your project's confirmed
conventions, and proving the replacement works by re-drawing a known circuit.

The payoff is that the skill stops producing generically-correct drawings and
starts producing drawings that match **your** house style - the one your
reviewers already expect.

Three axes matter, in this order:

| # | Axis | Why it matters |
|---|---|---|
| 1 | **Exemplar calibration** - learn from a schematic you drew | Fixes placement grammar, symmetry, routing, and annotation style |
| 2 | **Grid requirements** - your project's lattice | Every coordinate rule in the skill derives from this |
| 3 | **Note requirements** - your project's annotation convention | Determines whether a drawing reads as finished to your reviewers |

Calibrate in that order. A grid change invalidates earlier geometry
comparisons, so settle the lattice before you iterate on style.

---

## 1. Exemplar Calibration - The 5T OTA Loop

### Why A Five-Transistor OTA

A 5T OTA (differential pair, tail current source, mirror load, supply and ground
rails) is the recommended calibration vehicle because:

- it is small enough to inspect completely - five devices, no ambiguity about
  whether you missed something;
- it contains **every structure this skill has an opinion about**: differential
  pair symmetry, a current-mirror trunk, a tail device against a rail, and
  power/ground placement;
- you already know what a correct one looks like in your project, so you can act
  as the ground truth without preparation.

### The Loop

```
Round 0  Ask the AI to draw a 5T OTA with the skill as-is. Save it, change
         nothing. This is your baseline, and it will not be good yet.

Round 1..N
         a. Put your own 5T OTA and the AI's drawing side by side.
         b. List every visible difference. Do not fix anything while listing.
         c. Sort each difference into one class:
              placement grammar | symmetry | routing | annotation |
              pin banks | naming
         d. Decide, per difference: project convention, or one-off?
         e. Record only the project conventions into the skill.
         f. Run from scratch again and compare.
```

### Why More Than One Round

One round cannot surface everything, because each class is only visible once the
previous one is settled. In practice the rounds tend to look like this:

| Round | What usually surfaces |
|---|---|
| 1 | gross placement - devices in the wrong relative order, island boundaries wrong |
| 2 | symmetry - mirror orientation, which device is mirrored, axis position |
| 3 | routing - crossings, wires through bodies, trunk vs labels |
| 4 | annotation - label placement, text height, which notes are expected |
| 5+ | pin banks, hierarchy boundaries, naming - usually the last to stabilise |

Stop when a **fresh run** reproduces your exemplar's **grammar** with no
human-corrected difference in the class you are testing. Not when the coordinates
match - they should not.

### What To Compare

Compare these, in this order. Earlier items dominate later ones:

1. **Relative order** of devices along the signal path.
2. **Functional island boundaries** - which devices are grouped together.
3. **Symmetry axis and mirror orientation** for each matched pair.
4. **Which relationships are drawn as wires** versus named by a label.
5. **Rail placement** - supply at top, ground at bottom, and how many rail runs.
6. **Annotation** - what text is present, where it sits, how large it is.
7. **Pin bank layout** - side, order, pitch.

### What To Record, And Where

| Finding | Where it goes |
|---|---|
| A correct region you want preserved as-is | the protected-exemplar contract in `references/compact-functional-block-style.md` |
| A placement rule ("mirrors sit left of the pair") | the placement grammar section of the same file |
| A routing rule ("mirror gates use one trunk, never repeated labels") | your project's routing notes; the skill's `## Route And Label` is the model |
| An annotation rule | `CALIBRATION` axis 3 below, then the frame/annotation section of `SKILL.md` |

### Cautions

- **Do not teach absolute coordinates.** The skill's own rule is to copy visual
  relationships and object roles, not coordinates or dimensions. Teaching
  coordinates overfits the skill to one cell and it will misdraw the next one.
- **Do not generalise from one circuit.** A convention you extracted from a 5T
  OTA may not hold for a power stage or a digital cell. Confirm it on a second
  topology before writing it in as a hard rule.
- **Keep your exemplar protected.** Once you mark a region as correct, adjacent
  automated cleanup must not redraw it. The skill's protected-example contract
  exists for this; use it rather than re-explaining the style each session.
- **Separate style from correctness.** If a difference is electrical rather than
  visual, it is not a calibration item - it is a bug to report and fix first.

---

## 2. Grid Requirements

Every geometry rule in this skill derives from the grid. If your grid differs
from the defaults, nothing else will land correctly until you declare it.

### Declare These

| Item | Example | Notes |
|---|---|---|
| Coordinate quantum | `0.0625` | the lattice every coordinate must land on |
| Pin-bank pitch | `0.125` (= 2 quanta) | compact same-direction external banks only |
| Label text height | `0.0625` | one height for one class of labels |
| Half-grid allowed? | no | some tools snap to half a quantum; if allowed, say so explicitly |
| Origin / reference convention | view origin | what "on grid" is measured relative to |
| Legacy off-grid pins | preserve, report | never silently snap a protected pin |

### Recording Template

```text
Project grid override
  quantum            : 0.0625
  pin bank pitch     : 0.125
  label height       : 0.0625
  half grid allowed  : no
  origin             : view origin
  legacy off-grid    : preserve and report, never snap
  confirmed by       : <name>, <date>
```

Write this into the **Project Grid Overrides** section of `SKILL.md`. That
section already states that a confirmed project grid takes priority over the
generic defaults in the same file.

### Traps Learned The Hard Way

- **Digit confusion is a real failure mode.** A grid of `0.625` and one of
  `0.0625` differ by 10x, and both look plausible. Confirm the number against
  the actual tool, not against a note you wrote earlier.
- **Serialisation precision is not grid evidence.** A coordinate formatted to
  six decimals does not prove it is on the lattice. Assert it numerically.
- **Snapping can create a topology change.** Re-run contact analysis after
  snapping; a snap that introduces a touch or a merge must stop the operation.
- **A hard-coded literal is not a convention.** A value that happens to read
  `0.0625` is not proof the author intended that grid.

---

## 3. Note Requirements

"Notes" covers two different things, and a project usually has rules for both:
annotations **inside** the drawing, and notes **about** the drawing.

### 3a. In-Drawing Annotations

| Question | Why it needs an answer |
|---|---|
| Are functional-island frames required, optional, or forbidden? | Determines whether a drawing reads as finished |
| Frame style - line weight, padding, corner style | Reviewers notice inconsistency immediately |
| Where does the block note go - above, below, outside corner? | Mixed placement is the most common frame defect |
| Note language - English, Chinese, or mixed? | A project requirement, not a style preference |
| Is a revision or date required on the drawing? | Some projects require it, some forbid it |
| Are net-name labels required on rails, or only on signals? | Affects label density and the score's annotation category |
| Is a symbol title required? | Some symbol conventions require it; deleting it to save space is a defect |
| Which layer is used for non-electrical frames and notes? | Frames must carry no net and no connectivity meaning |

### 3b. Delivery Notes

| Question | Why |
|---|---|
| What must the completion report contain? | Determines what evidence you can actually claim |
| Is the two-layer split (gates vs score) reported separately? | This skill requires it; do not merge them into one verdict |
| Are unresolved findings listed explicitly? | A "clean" report that hides a remaining gap is worse than a short honest one |
| Naming convention for delivered artifacts | Keeps handoffs traceable |

### Recording Template

```text
Project note override
  island frames      : required, dashed, 4pt corner, one grid padding
  block note position: below the frame, left-aligned
  note language      : English
  revision on drawing: required, bottom-right
  symbol title       : required, keep on shrink
  non-electrical LPP : <layer>, no net, no connectivity
  report must contain: gate result, score, render review, unresolved findings
```

### Cautions

- **A note must never cover geometry.** If a note collides with a wire, a label,
  or a symbol, fix the note or the geometry - never shrink the text to hide it.
- **Frames are not electrical.** Putting a frame on a conductive layer, or
  letting it carry a net, creates a false connection risk.
- **Do not let annotations substitute for topology.** A note explaining what a
  block does is not a replacement for drawing the block's internal
  relationships explicitly.

---

## Where Your Calibration Lives

Keep your three overrides in one place so they survive a skill update:

| Axis | File | Section |
|---|---|---|
| Grid | `SKILL.md` | Project Grid Overrides |
| Exemplar / placement | `references/compact-functional-block-style.md` | Protected-Example Contract, Placement Grammar |
| Notes | `SKILL.md` | Frame And Annotate Functional Blocks |

When you pull a newer version of this skill, re-apply your overrides. They are
deliberately written as declarations in named sections so a merge is mechanical
rather than archaeological.

## What Not To Do

- Do not treat the shipped weight table as measured truth. Weights marked
  `[calibrated]` are starting points; replace them and say so.
- Do not calibrate against a drawing you are not confident in. You will encode
  your own accident as a convention.
- Do not skip round 0. Without a recorded baseline you cannot tell whether a
  later change helped or whether the circuit simply got easier.
- Do not calibrate style before the grid. A grid change moves everything.

## Honest Limits

Calibration makes this skill match your project. It does not make the skill
verify your circuit, and it does not transfer your conventions to another
process - a PDK change or a different project should trigger a fresh
calibration, at least on axis 1.
