"""
Kiosk speaker plinth for the AboveTEK countertop tablet stand + Anker Soundcore 2.

The stand's base nests in a recess on top of a hollow plinth. The speaker sits in a
front cradle (top buttons stay fully exposed) with an open-floor "port bay" at the
flap end so the Micro-USB and AUX plugs can stay connected and drop into the hidden
cavity. A USB splitter / spare cable lives in the cavity; one input cable exits the back.

Run:  python kiosk_speaker_mount.py   -> writes STEP + STL files to ./output
All dimensions are in millimetres. Coordinates: X across (centered), Y front->back
(front face at Y=0), Z up (bottom of plinth at Z=0).
"""

from pathlib import Path

import cadquery as cq

# ---------------------------------------------------------------- parameters
# Stand base (from product image; MEASURE AND UPDATE)
STAND_BASE_W = 175.0  # side to side
STAND_BASE_D = 160.0  # front to back
STAND_BASE_T = 4.0  # steel plate thickness (= recess depth, base sits flush)
STAND_BASE_R = 10.0  # base corner radius
# Optional bolt-through holes matching the stand's base holes, (x, y) from the
# stand-base center (+y toward the back). Example: [(-60, -50), (60, -50), (-60, 50), (60, 50)]
STAND_HOLES: list[tuple[float, float]] = []
STAND_HOLE_D = 4.5

# Speaker (Anker Soundcore 2: 6.5 x 1.77 x 2.13 in; MEASURE AND UPDATE)
SPK_L, SPK_D, SPK_H = 165.0, 45.0, 54.0
PORT_END = "right"  # end with the USB/AUX flap, as seen facing the grille: "right" or "left"
PORT_BAY = 32.0  # extra length at that end for plugs (right-angle plugs recommended)
FIT = 1.5  # clearance per side around speaker
STAND_FIT = 1.0  # clearance per side around stand base

# Plinth body
WALL = 3.0
TOP_T = 3.0  # thickness of the top deck / pocket floor
H = 38.0  # overall plinth height
POCKET_DEPTH = 20.0  # how far the speaker sits down into the plinth (top buttons stay clear)
FRONT_LIP = 8.0  # front lip height above pocket floor (keeps the grille exposed)
CORNER_R = 6.0

# Cable openings
TABLET_SLOT_W = 34.0  # rear-top notch for tablet charge + audio cables
TABLET_SLOT_D = 12.0
INPUT_NOTCH_W = 14.0  # rear-bottom notch for the single incoming cable
INPUT_NOTCH_H = 10.0
INPUT_NOTCH_X = 55.0
STRAP_SLOTS = True  # slots for an optional hook-and-loop strap at each speaker end
STRAP_W = 16.0
STRAP_T = 4.0
STRAP_X = 72.0  # strap offset from speaker center (kept outside the top buttons)

# Bottom cover + fasteners (M3 heat-set inserts)
COVER_T = 3.0
BOSS_D = 9.0
INSERT_HOLE_D = 4.0
INSERT_DEPTH = 6.0
SCREW_CLEAR_D = 3.4
CSK_D = 6.5
FOOT_D = 10.5  # recesses for stick-on rubber feet
FOOT_DEPTH = 1.0
FOOT_INSET = 18.0

# Internal support ribs (let the plinth print right-side up without supports).
# Ribs run side to side; pointed-arch openings print without supports and pass cables.
RIB_T = 2.0
DECK_RIBS = 3  # ribs under the stand deck
DECK_RIB_OPENINGS_X = (-60.0, 0.0, 60.0)
DECK_RIB_OPENING_W = 40.0
DIVIDER_OPENING_W = 20.0  # openings in the rib under the cradle's back wall
ARCH_CLEARANCE = 3.0  # min material between arch peak and ceiling

OUT_DIR = Path(__file__).parent / "output"

# ---------------------------------------------------------------- derived
pocket_w = SPK_D + 2 * FIT
spk_len = SPK_L + 2 * FIT
pocket_len = spk_len + PORT_BAY
recess_w = STAND_BASE_W + 2 * STAND_FIT
recess_d = STAND_BASE_D + 2 * STAND_FIT

W = max(pocket_len, recess_w) + 2 * WALL
D = 3 * WALL + pocket_w + recess_d

pocket_y0, pocket_y1 = WALL, WALL + pocket_w
recess_y0 = pocket_y1 + WALL
recess_y1 = recess_y0 + recess_d
recess_cy = (recess_y0 + recess_y1) / 2

pocket_floor_z = H - POCKET_DEPTH
cavity_a_top = pocket_floor_z - TOP_T  # under the speaker
cavity_b_top = H - STAND_BASE_T - TOP_T  # under the stand

if PORT_END == "right":
    spk_x0, spk_x1 = -pocket_len / 2, -pocket_len / 2 + spk_len
    bay_x0, bay_x1 = spk_x1, pocket_len / 2
else:
    spk_x0, spk_x1 = pocket_len / 2 - spk_len, pocket_len / 2
    bay_x0, bay_x1 = -pocket_len / 2, spk_x0
spk_cx = (spk_x0 + spk_x1) / 2

boss_inset = WALL + BOSS_D / 2 - 1.0
bx = W / 2 - boss_inset
# Front bosses avoid the port bay and strap slots: one at front-center, two just behind the cradle
BOSS_PTS = [
    (spk_cx, boss_inset),
    (-bx, recess_y0 + boss_inset),
    (bx, recess_y0 + boss_inset),
    (-bx, recess_cy),
    (bx, recess_cy),
    (-bx, D - boss_inset),
    (bx, D - boss_inset),
]


def box(x0, x1, y0, y1, z0, z1):
    return (
        cq.Workplane("XY")
        .box(x1 - x0, y1 - y0, z1 - z0, centered=False)
        .translate((x0, y0, z0))
    )


def cyl(x, y, d, z0, z1):
    return cq.Workplane("XY").workplane(offset=z0).center(x, y).circle(d / 2).extrude(z1 - z0)


def arch_rib(y0, y1, top, openings_x, opening_w):
    """Side-to-side rib from the floor to `top`, with pointed-arch (45 deg roof) openings."""
    rib = box(-W / 2 + WALL - 0.5, W / 2 - WALL + 0.5, y0, y1, 0, top + 0.5)
    half = opening_w / 2
    shoulder = max(0.0, top - ARCH_CLEARANCE - half)
    for x in openings_x:
        arch = (
            cq.Workplane("XZ")
            .polyline([(x - half, -1), (x + half, -1), (x + half, shoulder), (x, shoulder + half), (x - half, shoulder)])
            .close()
            .extrude((y1 - y0) / 2 + 1, both=True)
            .translate((0, (y0 + y1) / 2, 0))
        )
        rib = rib.cut(arch)
    return rib


def build_ribs():
    divider_openings = ((bay_x0 + bay_x1) / 2, spk_cx - 40, spk_cx + 40)
    ribs = arch_rib(pocket_y1, recess_y0, cavity_a_top, divider_openings, DIVIDER_OPENING_W)
    span = (D - WALL) - recess_y0
    for i in range(1, DECK_RIBS + 1):
        y = recess_y0 + i * span / (DECK_RIBS + 1)
        ribs = ribs.union(arch_rib(y - RIB_T / 2, y + RIB_T / 2, cavity_b_top, DECK_RIB_OPENINGS_X, DECK_RIB_OPENING_W))
    return ribs


def build_plinth():
    body = cq.Workplane("XY").box(W, D, H, centered=(True, False, False)).edges("|Z").fillet(CORNER_R)

    # Hidden cavity (open bottom), minus screw bosses so they stay solid
    cavity = box(-W / 2 + WALL, W / 2 - WALL, WALL, D - WALL, -1, cavity_a_top).union(
        box(-W / 2 + WALL, W / 2 - WALL, recess_y0, D - WALL, -1, cavity_b_top)
    )
    for x, y in BOSS_PTS:
        cavity = cavity.cut(cyl(x, y, BOSS_D, -2, H))
    body = body.cut(cavity).union(build_ribs())

    # Stand base recess
    recess = (
        cq.Workplane("XY")
        .workplane(offset=H - STAND_BASE_T)
        .center(0, recess_cy)
        .rect(recess_w, recess_d)
        .extrude(STAND_BASE_T + 1)
        .edges("|Z")
        .fillet(STAND_BASE_R)
    )
    body = body.cut(recess)

    # Speaker cradle + port bay (open top keeps the buttons accessible)
    body = body.cut(box(-pocket_len / 2, pocket_len / 2, pocket_y0, pocket_y1, pocket_floor_z, H + 1))
    # Lower front lip so the grille is exposed
    body = body.cut(box(-pocket_len / 2, pocket_len / 2, -1, pocket_y0 + 0.01, pocket_floor_z + FRONT_LIP, H + 1))
    # Open floor in the port bay so connected plugs/cables drop into the cavity
    body = body.cut(box(bay_x0, bay_x1, pocket_y0, pocket_y1, cavity_a_top - 1, pocket_floor_z + 1))

    if STRAP_SLOTS:
        for dx in (-STRAP_X, STRAP_X):
            for y in (pocket_y0 + 0.5, pocket_y1 - 0.5 - STRAP_T):
                x = spk_cx + dx
                body = body.cut(box(x - STRAP_W / 2, x + STRAP_W / 2, y, y + STRAP_T, cavity_a_top - 1, pocket_floor_z + 1))

    # Rear-top notch for tablet cables (behind the stand upright)
    body = body.cut(box(-TABLET_SLOT_W / 2, TABLET_SLOT_W / 2, D - WALL - TABLET_SLOT_D, D + 1, cavity_b_top - 1, H + 1))
    # Rear-bottom notch for the single incoming cable
    body = body.cut(box(INPUT_NOTCH_X - INPUT_NOTCH_W / 2, INPUT_NOTCH_X + INPUT_NOTCH_W / 2, D - WALL - 1, D + 1, -1, INPUT_NOTCH_H))

    # Heat-set insert holes in the bosses
    for x, y in BOSS_PTS:
        body = body.cut(cyl(x, y, INSERT_HOLE_D, -1, INSERT_DEPTH))

    for x, y in STAND_HOLES:
        body = body.cut(cyl(x, recess_cy + y, STAND_HOLE_D, cavity_b_top - 1, H + 1))

    return body


def build_cover():
    cover = (
        cq.Workplane("XY")
        .box(W, D, COVER_T, centered=(True, False, False))
        .edges("|Z")
        .fillet(CORNER_R)
        .translate((0, 0, -COVER_T))
    )
    # Workplane on the underside: local y = -global y
    bottom = cq.Plane(origin=(0, 0, -COVER_T), xDir=(1, 0, 0), normal=(0, 0, -1))
    cover = cover.copyWorkplane(cq.Workplane(bottom)).pushPoints([(x, -y) for x, y in BOSS_PTS]).cskHole(SCREW_CLEAR_D, CSK_D, 90)

    for x in (-W / 2 + FOOT_INSET, W / 2 - FOOT_INSET):
        for y in (FOOT_INSET, D - FOOT_INSET):
            cover = cover.cut(cyl(x, y, FOOT_D, -COVER_T - 1, -COVER_T + FOOT_DEPTH))

    for x, y in STAND_HOLES:
        cover = cover.cut(cyl(x, recess_cy + y, STAND_HOLE_D, -COVER_T - 1, 1))

    return cover


def build_reference_speaker():
    return (
        cq.Workplane("XY")
        .box(SPK_L, SPK_D, SPK_H, centered=(True, True, False))
        .edges("|Y")
        .fillet(8)
        .translate((spk_cx, (pocket_y0 + pocket_y1) / 2, pocket_floor_z))
    )


def build_reference_stand_base():
    return (
        cq.Workplane("XY")
        .rect(STAND_BASE_W, STAND_BASE_D)
        .extrude(STAND_BASE_T)
        .edges("|Z")
        .fillet(STAND_BASE_R)
        .translate((0, recess_cy, H - STAND_BASE_T))
    )


def main():
    OUT_DIR.mkdir(exist_ok=True)
    plinth = build_plinth()
    cover = build_cover()
    spk = build_reference_speaker()
    stand = build_reference_stand_base()

    for name, part in (("plinth", plinth), ("bottom_cover", cover)):
        assert part.val().isValid(), f"{name} is not a valid solid"
        cq.exporters.export(part, str(OUT_DIR / f"{name}.step"))
        cq.exporters.export(part, str(OUT_DIR / f"{name}.stl"), tolerance=0.05, angularTolerance=0.1)

    asm = (
        cq.Assembly(name="kiosk_speaker_mount")
        .add(plinth, name="plinth", color=cq.Color(0.2, 0.2, 0.22))
        .add(cover, name="bottom_cover", color=cq.Color(0.35, 0.35, 0.38))
        .add(spk, name="ref_soundcore2", color=cq.Color(0.1, 0.3, 0.7, 0.6))
        .add(stand, name="ref_stand_base", color=cq.Color(0.7, 0.7, 0.7, 0.6))
    )
    asm.export(str(OUT_DIR / "assembly_with_references.step"))

    print(f"Plinth footprint: {W:.1f} x {D:.1f} mm, height {H:.1f} mm (+{COVER_T:.1f} mm cover)")
    print(f"Cavity height: {cavity_a_top:.1f} mm under speaker, {cavity_b_top:.1f} mm under stand")
    print(f"Wrote files to {OUT_DIR}")


if __name__ == "__main__":
    main()
