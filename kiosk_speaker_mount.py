"""
Kiosk speaker cradle for the AboveTEK countertop tablet stand + Anker Soundcore 2.

The speaker sits in a cradle on the front of the stand's base plate, below the tablet,
grille facing the customer. A tongue on the back of the cradle passes through the oval
cutout in the stand's upright and is screwed (security Torx) to a rear box on the staff
side, clamping the steel plate between them: the parts can't be separated without the
driver. The speaker's USB/AUX plugs stay connected in an enclosed port bay at the flap
end; the cables run through a channel behind the speaker and through the tongue into
the rear box, which hides a USB splitter. One input cable exits the rear box.

Run:  python kiosk_speaker_mount.py   -> checks the fit, writes STEP + STL files to ./output
All dimensions are in millimetres. Coordinates: X across (0 = center of the oval cutout),
Y front->back (0 = front face of the stand's upright), Z up (0 = counter top).
"""

from pathlib import Path

import cadquery as cq

# ---------------------------------------------------------------- parameters
# Stand (AboveTEK, scaled from product photos; MEASURE AND UPDATE).
# One bent steel sheet: the base plate runs forward under the tablet and curves up
# at its back edge into the upright.
PLATE_T = 4.0  # steel sheet thickness (base and upright; what the clamp grips)
BASE_W = 175.0  # base plate width
BASE_R = 10.0  # base plate front corner radius
BASE_FRONT = 150.0  # from the base plate's front edge back to the upright's front face
BEND_R = 25.0  # inside radius where the base plate curves up into the upright
STAND_H = 165.0  # counter to the tablet-clamp pivot
# Upright outline as (height above counter, half-width) pairs, bottom to top
UPRIGHT_PROFILE = [(0.0, 87.5), (15.0, 60.0), (40.0, 45.0), (80.0, 35.0), (120.0, 28.0), (STAND_H, 28.0)]
OVAL_W = 38.0  # oval cutout width
OVAL_Z0, OVAL_Z1 = 2.0, 92.0  # oval cutout bottom and top, above the counter
TABLET_CLEAR_Z = 76.0  # counter to the tablet's lowest edge; every part must stay below this

# Speaker (Anker Soundcore 2: 6.5 x 1.77 x 2.13 in; MEASURE AND UPDATE)
SPK_L, SPK_D, SPK_H = 165.0, 45.0, 54.0
PORT_END = "right"  # end with the USB/AUX flap, as seen facing the grille: "right" or "left"
PORT_BAY = 32.0  # extra length at that end for plugs (right-angle plugs recommended)
FIT = 1.5  # clearance per side around speaker
STAND_FIT = 1.0  # clearance around the stand's bend

# Cradle
WALL = 3.0
FLOOR_T = 6.0  # cradle floor; rests on the base plate and holds the strap grooves underneath
POCKET_DEPTH = 20.0  # how far the speaker sits down into the cradle (top buttons stay clear)
FRONT_LIP = 8.0  # front lip height above the floor (keeps the grille exposed)
CORNER_R = 6.0
CLAMP_WALL_T = 5.0  # cradle back wall that presses on the upright (holds the tongue inserts)
CHANNEL_D = 12.0  # cable channel behind the speaker, front to back
STRAP_SLOTS = True  # slots for an optional hook-and-loop strap at each speaker end
STRAP_W = 16.0
STRAP_T = 4.0
STRAP_X = 72.0  # strap offset from speaker center (kept outside the top buttons)

# Clamp through the oval: M3 heat-set inserts in the tongue, M3 security Torx screws from the rear box
TONGUE_Z0, TONGUE_Z1 = 34.0, 60.0  # tongue bottom and top, above the counter
OVAL_FIT = 1.0  # clearance between the tongue and the oval
CLAMP_GAP = 0.5  # tongue is this much shorter than PLATE_T so the screws pull both parts onto the plate
PASS_W, PASS_H = 14.0, 14.0  # cable passage through the tongue and the rear box front wall
CLAMP_SCREW_X = 13.5  # clamp screws at +/- this X, at tongue mid-height
INSERT_HOLE_D = 4.0
INSERT_DEPTH = 6.0
SCREW_CLEAR_D = 3.4

# Rear box (staff side; hides the USB splitter)
SPLITTER_L, SPLITTER_W, SPLITTER_H = 60.0, 30.0, 20.0  # splitter length (X), width (Z), thickness (Y); MEASURE
REAR_WALL = 3.0
LID_T = 3.0
LID_BOSS_D = 8.0
TABLET_SLOT_W = 20.0  # top notch: tablet charge + AUX cables up to the tablet
INPUT_NOTCH_W = 10.0  # bottom notch: the single incoming cable
CABLE_NOTCH_D = 10.0  # how far both notches reach in from the lid edge

OUT_DIR = Path(__file__).parent / "output"

# ---------------------------------------------------------------- derived
oval_cz = (OVAL_Z0 + OVAL_Z1) / 2
oval_h = OVAL_Z1 - OVAL_Z0

pocket_w = SPK_D + 2 * FIT
spk_len = SPK_L + 2 * FIT
pocket_len = spk_len + PORT_BAY
W = pocket_len + 2 * WALL

# Back section between the speaker and the upright; at least deep enough that the
# pocket floor (and the strap grooves under it) end a wall's thickness in front of the bend clearance
spine_d = max(CLAMP_WALL_T + CHANNEL_D + WALL, BEND_R + STAND_FIT + WALL)
pocket_y1 = -spine_d
pocket_y0 = pocket_y1 - pocket_w
cradle_y0 = pocket_y0 - WALL
channel_y0, channel_y1 = -CLAMP_WALL_T - CHANNEL_D, -CLAMP_WALL_T

floor_z = PLATE_T + FLOOR_T  # speaker bottom
rim_z = floor_z + POCKET_DEPTH
tongue_cz = (TONGUE_Z0 + TONGUE_Z1) / 2
tongue_y1 = PLATE_T - CLAMP_GAP
back_z = TONGUE_Z1 + WALL  # top of the back section and the port-bay walls
pass_z0, pass_z1 = tongue_cz - PASS_H / 2, tongue_cz + PASS_H / 2

if PORT_END == "right":
    spk_x0, spk_x1 = -pocket_len / 2, -pocket_len / 2 + spk_len
    bay_x0, bay_x1 = spk_x1, pocket_len / 2
    ch_x0, ch_x1 = -PASS_W / 2, bay_x0 + 1
else:
    spk_x0, spk_x1 = pocket_len / 2 - spk_len, pocket_len / 2
    bay_x0, bay_x1 = -pocket_len / 2, spk_x0
    ch_x0, ch_x1 = bay_x1 - 1, PASS_W / 2
spk_cx = (spk_x0 + spk_x1) / 2

CLAMP_PTS = [(-CLAMP_SCREW_X, tongue_cz), (CLAMP_SCREW_X, tongue_cz)]  # (x, z)

rear_in_w = SPLITTER_L + 2 * (LID_BOSS_D + 1)
rear_in_h = SPLITTER_W + 6
rear_in_d = SPLITTER_H + 4
rear_w = rear_in_w + 2 * REAR_WALL
rear_y0 = PLATE_T
rear_y1 = rear_y0 + REAR_WALL + rear_in_d  # open back, closed by the lid
rear_z0 = PLATE_T + BEND_R + STAND_FIT  # clears the bend behind the upright
rear_z1 = rear_z0 + rear_in_h + 2 * REAR_WALL
lid_bx = rear_in_w / 2 - LID_BOSS_D / 2 + 1
LID_PTS = [  # (x, z), diagonal corners
    (-lid_bx, rear_z0 + REAR_WALL + LID_BOSS_D / 2 - 1),
    (lid_bx, rear_z1 - REAR_WALL - LID_BOSS_D / 2 + 1),
]


def box(x0, x1, y0, y1, z0, z1):
    return (
        cq.Workplane("XY")
        .box(x1 - x0, y1 - y0, z1 - z0, centered=False)
        .translate((x0, y0, z0))
    )


def cyl(x, y, d, z0, z1):
    return cq.Workplane("XY").workplane(offset=z0).center(x, y).circle(d / 2).extrude(z1 - z0)


def cyl_x(y, z, d, x0, x1):
    return cq.Workplane("YZ").center(y, z).circle(d / 2).extrude(x1 - x0).translate((x0, 0, 0))


def cyl_y(x, z, d, y0, y1):
    return cq.Workplane("XZ").center(x, z).circle(d / 2).extrude(y1 - y0).translate((0, y1, 0))


def xz_prism(sketch, y0, y1):
    """Extrude a closed sketch drawn on Workplane("XZ") (local x = X, local y = Z) from Y=y0 to Y=y1."""
    return sketch.extrude(y1 - y0).translate((0, y1, 0))


def yz_prism(pts, x0, x1):
    """Extrude a (y, z) polygon from X=x0 to X=x1."""
    return cq.Workplane("YZ").polyline(pts).close().extrude(x1 - x0).translate((x0, 0, 0))


def upright_outline():
    pts = [(hw, z) for z, hw in UPRIGHT_PROFILE] + [(-hw, z) for z, hw in reversed(UPRIGHT_PROFILE)]
    return cq.Workplane("XZ").polyline(pts).close()


def oval_sketch(inset=0.0):
    return cq.Workplane("XZ").center(0, oval_cz).ellipse(OVAL_W / 2 - inset, oval_h / 2 - inset)


def build_cradle():
    tray = box(-W / 2, W / 2, cradle_y0, 0, PLATE_T, rim_z).edges("|Z").fillet(CORNER_R)
    spine = box(-W / 2, W / 2, pocket_y1, 0, PLATE_T, back_z).edges("|Z").fillet(CORNER_R)
    # Full-height walls around the port bay hide the plugs from the front
    hx0, hx1, outer = (bay_x0, W / 2, ">X") if PORT_END == "right" else (-W / 2, bay_x1, "<X")
    hood = box(hx0, hx1, cradle_y0, 0, PLATE_T, back_z).edges("|Z").edges(outer).fillet(CORNER_R)
    body = tray.union(spine).union(hood)

    # Speaker pocket + port bay (open top keeps the buttons accessible)
    body = body.cut(box(-pocket_len / 2, pocket_len / 2, pocket_y0, pocket_y1, floor_z, back_z + 1))
    # Lower front lip along the speaker so the grille is exposed
    body = body.cut(box(spk_x0, spk_x1, cradle_y0 - 1, pocket_y0 + 0.01, floor_z + FRONT_LIP, back_z + 1))
    # Port bay opens back into the cable channel
    body = body.cut(box(bay_x0, bay_x1, pocket_y1 - 1, channel_y1, floor_z, back_z + 1))
    # Cable channel behind the speaker, from the bay to the tongue
    body = body.cut(box(ch_x0, ch_x1, channel_y0, channel_y1, pass_z0, pass_z1))

    # Tongue through the oval, with a cable passage and the clamp-screw inserts
    tongue = xz_prism(oval_sketch(OVAL_FIT), -CLAMP_WALL_T, tongue_y1).intersect(
        box(-W / 2, W / 2, -CLAMP_WALL_T - 1, tongue_y1 + 1, TONGUE_Z0, TONGUE_Z1)
    )
    body = body.union(tongue)
    body = body.cut(box(-PASS_W / 2, PASS_W / 2, channel_y0 + 1, tongue_y1 + 1, pass_z0, pass_z1))
    for x, z in CLAMP_PTS:
        body = body.cut(cyl_y(x, z, INSERT_HOLE_D, tongue_y1 - INSERT_DEPTH, tongue_y1 + 1))

    # 45 deg chamfer under the back clears the stand's bend and prints without supports
    k = BEND_R + STAND_FIT
    body = body.cut(yz_prism([(-k - 1, PLATE_T - 1), (1, PLATE_T - 1), (1, PLATE_T + k + 1)], -W / 2 - 1, W / 2 + 1))

    if STRAP_SLOTS:
        fy0, fy1 = pocket_y0 + 0.5, pocket_y1 - 0.5
        for dx in (-STRAP_X, STRAP_X):
            x0, x1 = spk_cx + dx - STRAP_W / 2, spk_cx + dx + STRAP_W / 2
            # Groove under the floor joins a slot at the front and back of the pocket
            body = body.cut(box(x0, x1, fy0, fy1, PLATE_T - 1, PLATE_T + STRAP_T))
            for y in (fy0, fy1 - STRAP_T):
                body = body.cut(box(x0, x1, y, y + STRAP_T, PLATE_T - 1, floor_z + 1))

    return body


def build_rear_box():
    shell = box(-rear_w / 2, rear_w / 2, rear_y0, rear_y1, rear_z0, rear_z1).edges("|Y").fillet(CORNER_R)
    shell = shell.cut(
        box(-rear_in_w / 2, rear_in_w / 2, rear_y0 + REAR_WALL, rear_y1 + 1, rear_z0 + REAR_WALL, rear_z1 - REAR_WALL)
    )
    for x, z in LID_PTS:
        shell = shell.union(cyl_y(x, z, LID_BOSS_D, rear_y0 + REAR_WALL - 0.5, rear_y1))
        shell = shell.cut(cyl_y(x, z, INSERT_HOLE_D, rear_y1 - INSERT_DEPTH, rear_y1 + 1))

    # Front wall: cable passage + clamp screw holes (screw heads sit inside the box, under the lid)
    shell = shell.cut(box(-PASS_W / 2, PASS_W / 2, rear_y0 - 1, rear_y0 + REAR_WALL + 1, pass_z0, pass_z1))
    for x, z in CLAMP_PTS:
        shell = shell.cut(cyl_y(x, z, SCREW_CLEAR_D, rear_y0 - 1, rear_y0 + REAR_WALL + 1))

    # Cable notches, open at the lid edge
    shell = shell.cut(box(-TABLET_SLOT_W / 2, TABLET_SLOT_W / 2, rear_y1 - CABLE_NOTCH_D, rear_y1 + 1,
                          rear_z1 - REAR_WALL - 1, rear_z1 + 1))
    shell = shell.cut(box(-INPUT_NOTCH_W / 2, INPUT_NOTCH_W / 2, rear_y1 - CABLE_NOTCH_D, rear_y1 + 1,
                          rear_z0 - 1, rear_z0 + REAR_WALL + 1))
    return shell


def build_rear_lid():
    lid = box(-rear_w / 2, rear_w / 2, rear_y1, rear_y1 + LID_T, rear_z0, rear_z1).edges("|Y").fillet(CORNER_R)
    for x, z in LID_PTS:
        lid = lid.cut(cyl_y(x, z, SCREW_CLEAR_D, rear_y1 - 1, rear_y1 + LID_T + 1))
    return lid


def build_reference_speaker():
    return (
        cq.Workplane("XY")
        .box(SPK_L, SPK_D, SPK_H, centered=(True, True, False))
        .edges("|Y")
        .fillet(8)
        .translate((spk_cx, (pocket_y0 + pocket_y1) / 2, floor_z))
    )


def build_reference_stand():
    """One bent sheet: flat base plate in front, a quarter-circle bend, then the upright."""
    hw0 = UPRIGHT_PROFILE[0][1]
    zc = PLATE_T + BEND_R
    base = (
        box(-BASE_W / 2, BASE_W / 2, -BASE_FRONT, -BEND_R, 0, PLATE_T)
        .edges("|Z")
        .edges("<Y")
        .fillet(BASE_R)
    )
    bend = (
        box(-hw0, hw0, -BEND_R, PLATE_T, 0, zc)
        .intersect(cyl_x(-BEND_R, zc, 2 * (BEND_R + PLATE_T), -hw0 - 1, hw0 + 1))
        .cut(cyl_x(-BEND_R, zc, 2 * BEND_R, -hw0 - 1, hw0 + 1))
    )
    upright = box(-hw0, hw0, 0, PLATE_T, zc, STAND_H)
    sheet = bend.union(upright).intersect(xz_prism(upright_outline(), -BEND_R - 1, PLATE_T + 1))

    oval = xz_prism(oval_sketch(), -BEND_R - 1, PLATE_T + 1)
    return base.union(sheet).cut(oval)


def check(cradle, rear, lid, spk, stand):
    """Fail loudly if parts overlap, holes don't line up, or anything reaches the tablet."""
    named = {"cradle": cradle, "rear_box": rear, "rear_lid": lid, "speaker": spk, "stand": stand}
    for name in ("cradle", "rear_box", "rear_lid"):
        assert named[name].val().isValid(), f"{name} is not a valid solid"
    pairs = [("cradle", "speaker"), ("cradle", "stand"), ("rear_box", "stand"), ("rear_box", "cradle"),
             ("rear_lid", "rear_box"), ("rear_lid", "stand"), ("speaker", "stand")]
    for a, b in pairs:
        vol = named[a].intersect(named[b]).val().Volume()
        assert vol < 1e-6, f"{a} overlaps {b} by {vol:.3f} mm^3"
    for x, z in CLAMP_PTS:
        assert not cradle.val().isInside(cq.Vector(x, tongue_y1 - 1, z)), f"no insert hole in tongue at {x, z}"
        assert not rear.val().isInside(cq.Vector(x, rear_y0 + REAR_WALL / 2, z)), f"no clamp screw hole at {x, z}"
    for x, z in LID_PTS:
        assert not rear.val().isInside(cq.Vector(x, rear_y1 - 1, z)), f"no lid insert hole at {x, z}"
        assert not lid.val().isInside(cq.Vector(x, rear_y1 + LID_T / 2, z)), f"no lid screw hole at {x, z}"
    top = max(floor_z + SPK_H, back_z, rear_z1)
    assert top < TABLET_CLEAR_Z, f"parts reach Z={top:.1f}, above the tablet's lowest edge ({TABLET_CLEAR_Z})"
    if cradle_y0 < -BASE_FRONT:
        print(f"WARNING: cradle front (Y={cradle_y0:.1f}) overhangs the base plate's front edge (Y={-BASE_FRONT:.1f})")


def main():
    OUT_DIR.mkdir(exist_ok=True)
    cradle = build_cradle()
    rear = build_rear_box()
    lid = build_rear_lid()
    spk = build_reference_speaker()
    stand = build_reference_stand()
    check(cradle, rear, lid, spk, stand)

    for name, part in (("cradle", cradle), ("rear_box", rear), ("rear_lid", lid)):
        cq.exporters.export(part, str(OUT_DIR / f"{name}.step"))
        cq.exporters.export(part, str(OUT_DIR / f"{name}.stl"), tolerance=0.05, angularTolerance=0.1)

    asm = (
        cq.Assembly(name="kiosk_speaker_mount")
        .add(cradle, name="cradle", color=cq.Color(0.2, 0.2, 0.22))
        .add(rear, name="rear_box", color=cq.Color(0.35, 0.35, 0.38))
        .add(lid, name="rear_lid", color=cq.Color(0.45, 0.45, 0.48))
        .add(spk, name="ref_soundcore2", color=cq.Color(0.1, 0.3, 0.7, 0.6))
        .add(stand, name="ref_stand", color=cq.Color(0.7, 0.7, 0.7, 0.6))
    )
    asm.export(str(OUT_DIR / "assembly_with_references.step"))

    print("Checks passed: no overlaps, all screw holes line up, clear of the tablet")
    print(f"Cradle: {W:.1f} x {-cradle_y0:.1f} mm footprint, {back_z:.1f} mm tall at the back")
    print(f"Rear box: {rear_w:.1f} x {rear_y1 + LID_T - rear_y0:.1f} x {rear_z1 - rear_z0:.1f} mm (W x D x H, with lid)")
    print(f"Speaker top at Z={floor_z + SPK_H:.1f} mm; tablet edge at Z={TABLET_CLEAR_Z:.1f} mm")
    print(f"Wrote files to {OUT_DIR}")


if __name__ == "__main__":
    main()
