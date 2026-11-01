"""
Kiosk speaker cradle for the AboveTEK countertop tablet stand + Anker Soundcore 2.

The speaker sits in a cradle on the front of the stand's base plate, below the tablet,
grille facing the customer. A tongue on the back of the cradle passes through the oval
cutout in the stand's upright and is screwed (security Torx) to a rear box on the staff
side, clamping the steel plate between them: the parts can't be separated without the
driver. The speaker slides in from the end opposite its ports, under two bars that stop
it being lifted out, until it hits an end stop; a screwed end gate then closes that end.
The speaker's USB/AUX plugs stay connected in a port bay at the flap end; the cables run
through a channel behind the speaker and through the tongue into the rear box, which
hides a USB splitter. One input cable exits the rear box.

Run:  python kiosk_speaker_mount.py   -> checks the fit, writes STEP + STL files to ./output
All dimensions are in millimetres. Coordinates: X across (0 = center of the oval cutout),
Y front->back (0 = where the upright's front face meets the top of the base plate, ignoring
the bend), Z up (0 = counter top). The upright leans toward the customer (-Y); parts on it
are built in a "plate frame" where it stands vertical, then tilted into place by tilt().
"""

import math
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
UPRIGHT_ANGLE = 75.0  # upright angle up from the counter; below 90 it leans toward the customer
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
CORE_LEN = 50.0  # hollow back section: longest cavity between cross ribs

# Speaker retention: bars over the speaker, an end stop at the port bay, and a screwed end gate
BAR_X = 72.0  # bars at +/- this X from the speaker center (kept outside the top buttons)
BAR_W = 12.0
BAR_T = 3.0  # bar thickness above the speaker
STOP_FIN = 5.0  # end-stop fins reach this far in from the front and back of the pocket
STOP_T = 3.0  # end-stop fin thickness
GATE_T = 4.0  # end gate plate thickness
GATE_FIT = 0.3  # clearance per side around the gate's plug in the end opening

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
LEAN = 90.0 - UPRIGHT_ANGLE  # degrees the upright leans toward the customer
_sin, _cos = math.sin(math.radians(LEAN)), math.cos(math.radians(LEAN))


def pz(z):
    """Plate-frame height of the point at counter height z on the upright's front face."""
    return PLATE_T + (z - PLATE_T) / _cos


def to_world(y, z):
    """Plate-frame (y, z) -> world (Y, Z). In the plate frame the upright is vertical, front face at y=0."""
    return y * _cos - (z - PLATE_T) * _sin, PLATE_T + y * _sin + (z - PLATE_T) * _cos


def face_y(z):
    """World Y of the upright's front face at counter height z."""
    return -(z - PLATE_T) * _sin / _cos


# Bend: its straight chord (from where it leaves the base plate to where the upright goes straight)
bend_t = BEND_R / math.tan(math.radians(UPRIGHT_ANGLE) / 2)  # tangent points, measured from the inner corner
bend_p0 = (-bend_t, PLATE_T)
bend_p1 = to_world(0, PLATE_T + bend_t)
_chord = math.dist(bend_p0, bend_p1)
bend_d = ((bend_p1[0] - bend_p0[0]) / _chord, (bend_p1[1] - bend_p0[1]) / _chord)  # up and back
bend_n = (-bend_d[1], bend_d[0])  # chord normal, toward the customer


def chamfer_y(z, off):
    """World Y at height z of the bend chord, moved `off` toward the customer."""
    y0, z0 = bend_p0[0] + off * bend_n[0], bend_p0[1] + off * bend_n[1]
    return y0 + (z - z0) * bend_d[0] / bend_d[1]


oval_cz = (pz(OVAL_Z0) + pz(OVAL_Z1)) / 2  # plate frame
oval_h = pz(OVAL_Z1) - pz(OVAL_Z0)

pocket_w = SPK_D + 2 * FIT
spk_len = SPK_L + 2 * FIT
pocket_len = spk_len + PORT_BAY
W = pocket_len + 2 * WALL

floor_z = PLATE_T + FLOOR_T  # speaker bottom
rim_z = floor_z + POCKET_DEPTH
tongue_cz = (TONGUE_Z0 + TONGUE_Z1) / 2
tongue_y1 = PLATE_T - CLAMP_GAP  # plate frame
back_z = TONGUE_Z1 + WALL  # top of the back section and the port-bay walls
pass_z0, pass_z1 = tongue_cz - PASS_H / 2, tongue_cz + PASS_H / 2  # cable channel heights
bar_z0 = floor_z + SPK_H + FIT
bar_z1 = bar_z0 + BAR_T

# Back section: a clamp wall against the leaning upright, the cable channel, then the speaker pocket,
# which also stays a wall's thickness in front of the bend clearance at floor level
channel_y1 = face_y(pass_z1) - CLAMP_WALL_T / _cos
channel_y0 = channel_y1 - CHANNEL_D
pocket_y1 = min(channel_y0 - WALL, chamfer_y(floor_z, STAND_FIT) - WALL)
pocket_y0 = pocket_y1 - pocket_w
cradle_y0 = pocket_y0 - WALL

if PORT_END == "right":
    spk_x0, spk_x1 = -pocket_len / 2, -pocket_len / 2 + spk_len
    bay_x0, bay_x1 = spk_x1, pocket_len / 2
    ch_x0, ch_x1 = -PASS_W / 2, bay_x0 + 1
    stop_x0, stop_x1 = spk_x1, spk_x1 + STOP_T
    gate_side = -1  # the speaker slides in from the end opposite the port bay
else:
    spk_x0, spk_x1 = pocket_len / 2 - spk_len, pocket_len / 2
    bay_x0, bay_x1 = -pocket_len / 2, spk_x0
    ch_x0, ch_x1 = bay_x1 - 1, PASS_W / 2
    stop_x0, stop_x1 = spk_x0 - STOP_T, spk_x0
    gate_side = 1
spk_cx = (spk_x0 + spk_x1) / 2
gate_x_out = gate_side * W / 2  # cradle end face behind the gate
gate_x_in = gate_side * pocket_len / 2  # inner face of the gate's plug
GATE_PT = (pocket_y1 + LID_BOSS_D / 2 + 2, rim_z - LID_BOSS_D / 2 - 1)  # (y, z) gate screw into the back section
gate_y1 = GATE_PT[0] + LID_BOSS_D / 2 + 1

# Clamp and rear box, in the plate frame
p_tongue_z0, p_tongue_z1, p_tongue_cz = pz(TONGUE_Z0), pz(TONGUE_Z1), pz(tongue_cz)
p_pass_z0, p_pass_z1 = p_tongue_cz - PASS_H / 2, p_tongue_cz + PASS_H / 2
CLAMP_PTS = [(-CLAMP_SCREW_X, p_tongue_cz), (CLAMP_SCREW_X, p_tongue_cz)]  # (x, plate-frame z)

rear_in_w = SPLITTER_L + 2 * (LID_BOSS_D + 1)
rear_in_h = SPLITTER_W + 6
rear_in_d = SPLITTER_H + 4
rear_w = rear_in_w + 2 * REAR_WALL
rear_y0 = PLATE_T
rear_y1 = rear_y0 + REAR_WALL + rear_in_d  # open back, closed by the lid
rear_z0 = PLATE_T + bend_t + STAND_FIT  # starts just above the bend
rear_z1 = rear_z0 + rear_in_h + 2 * REAR_WALL
lid_bx = rear_in_w / 2 - LID_BOSS_D / 2 + 1
LID_PTS = [  # (x, plate-frame z), diagonal corners
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
    """Oval cutout outline, in the plate frame."""
    return cq.Workplane("XZ").center(0, oval_cz).ellipse(OVAL_W / 2 - inset, oval_h / 2 - inset)


def tilt(wp):
    """Move a shape built in the plate frame (upright vertical) onto the leaning upright."""
    return wp.rotate((0, 0, PLATE_T), (1, 0, PLATE_T), LEAN)


def behind_face(x0, x1, inset=0.0):
    """Everything behind the upright's front face, or behind a plane `inset` in front of it."""
    return tilt(box(x0, x1, -inset, 300, -300, 400))


def bend_keepout(x0, x1, off):
    """Everything on the bend's side of its chord moved `off` toward the customer. The 45+ deg
    chamfer this leaves under the cradle contains the bend and prints without supports."""
    p0 = (bend_p0[0] + off * bend_n[0] - 10 * bend_d[0], bend_p0[1] + off * bend_n[1] - 10 * bend_d[1])
    p1 = (bend_p1[0] + off * bend_n[0] + 10 * bend_d[0], bend_p1[1] + off * bend_n[1] + 10 * bend_d[1])
    return yz_prism([p0, p1, (p1[0] + 300, p1[1]), (p1[0] + 300, p0[1])], x0, x1)


def core(x0, x1, z_top):
    """One closed cavity in the back section: 3 mm walls, a 45 deg peaked roof, and a clear
    CLAMP_WALL_T + WALL in front of the upright so the tongue's root stays solid."""
    ya = pocket_y1 + WALL
    yb = face_y(z_top) - (CLAMP_WALL_T + WALL) / _cos
    ym = (ya + yb) / 2
    c = box(x0, x1, ya, 0, PLATE_T + WALL, z_top)
    c = c.cut(bend_keepout(x0 - 1, x1 + 1, STAND_FIT + WALL)).cut(behind_face(x0 - 1, x1 + 1, CLAMP_WALL_T + WALL))
    return c.intersect(yz_prism([(ym - 100, z_top - 100), (ym, z_top), (ym + 100, z_top - 100)], x0 - 1, x1 + 1))


def core_cuts():
    """Cavities along the back section, split by cross ribs. They stay below the cable channel
    where it runs, and clear of the gate's insert and the port bay."""
    z_lo, z_hi = pass_z0 - 2 * WALL, back_z - WALL
    if PORT_END == "right":
        lo, hi = gate_x_out + INSERT_DEPTH + WALL, bay_x0 - WALL
        spans = [(lo, ch_x0 - 2 * WALL, z_hi), (ch_x0 - WALL, hi, z_lo)]
    else:
        lo, hi = bay_x1 + WALL, gate_x_out - INSERT_DEPTH - WALL
        spans = [(lo, ch_x1 + WALL, z_lo), (ch_x1 + 2 * WALL, hi, z_hi)]
    cuts = None
    for a, b, z_top in spans:
        n = max(1, math.ceil((b - a) / CORE_LEN))
        seg = (b - a - (n - 1) * WALL) / n
        for i in range(n):
            x0 = a + i * (seg + WALL)
            c = core(x0, x0 + seg, z_top)
            cuts = c if cuts is None else cuts.union(c)
    return cuts


def build_cradle():
    tray = box(-W / 2, W / 2, cradle_y0, 0, PLATE_T, rim_z).edges("|Z").fillet(CORNER_R)
    spine = box(-W / 2, W / 2, pocket_y1, 0, PLATE_T, back_z).edges("|Z").fillet(CORNER_R)
    # Full-height walls around the port bay hide the plugs from the front
    hx0, hx1, outer = (bay_x0, W / 2, ">X") if PORT_END == "right" else (-W / 2, bay_x1, "<X")
    hood = box(hx0, hx1, cradle_y0, 0, PLATE_T, back_z).edges("|Z").edges(outer).fillet(CORNER_R)
    body = tray.union(spine).union(hood)

    # Speaker pocket + port bay (open top keeps the buttons accessible)
    top = bar_z1 + 1
    body = body.cut(box(-pocket_len / 2, pocket_len / 2, pocket_y0, pocket_y1, floor_z, top))
    # Lower front lip along the speaker so the grille is exposed
    body = body.cut(box(spk_x0, spk_x1, cradle_y0 - 1, pocket_y0 + 0.01, floor_z + FRONT_LIP, top))
    # Port bay opens back into the cable channel
    body = body.cut(box(bay_x0, bay_x1, pocket_y1 - 1, channel_y1, floor_z, top))
    # Cable channel behind the speaker, from the bay to the tongue
    body = body.cut(box(ch_x0, ch_x1, channel_y0, channel_y1, pass_z0, pass_z1))
    # Open end where the speaker slides in; the end gate closes it
    body = body.cut(box(*sorted((gate_x_out + gate_side, gate_x_in)), pocket_y0, pocket_y1, floor_z, top))

    # Bars over both ends of the speaker stop it being lifted out; the top buttons between them stay clear
    for dx in (-BAR_X, BAR_X):
        x0, x1 = spk_cx + dx - BAR_W / 2, spk_cx + dx + BAR_W / 2
        body = body.union(box(x0, x1, cradle_y0, pocket_y0, PLATE_T, bar_z1))  # front post
        body = body.union(box(x0, x1, cradle_y0, 0, bar_z0, bar_z1))  # bar
        body = body.union(box(x0, x1, pocket_y1, 0, back_z - 1, bar_z1))  # joins the back section
    # End stop: fins at the front and back of the pocket keep the speaker out of the bay; plugs pass between
    for y0, y1 in ((pocket_y0, pocket_y0 + STOP_FIN), (pocket_y1 - STOP_FIN, pocket_y1)):
        body = body.union(box(stop_x0, stop_x1, y0, y1, floor_z, back_z))

    # Back follows the leaning upright; the chamfer underneath clears the bend
    body = body.cut(behind_face(-W, W)).cut(bend_keepout(-W, W, STAND_FIT))
    body = body.cut(core_cuts())

    # Tongue through the oval (plate frame), with a cable passage and the clamp-screw inserts
    tongue = xz_prism(oval_sketch(OVAL_FIT), -CLAMP_WALL_T, tongue_y1).intersect(
        box(-W / 2, W / 2, -CLAMP_WALL_T - 1, tongue_y1 + 1, p_tongue_z0, p_tongue_z1)
    )
    body = body.union(tilt(tongue))
    body = body.cut(tilt(box(-PASS_W / 2, PASS_W / 2, -CLAMP_WALL_T - CHANNEL_D / 2, tongue_y1 + 1,
                             p_pass_z0, p_pass_z1)))
    for x, z in CLAMP_PTS:
        body = body.cut(tilt(cyl_y(x, z, INSERT_HOLE_D, tongue_y1 - INSERT_DEPTH, tongue_y1 + 1)))

    # Insert for the end gate's screw
    gx = sorted((gate_x_out + gate_side, gate_x_out - gate_side * INSERT_DEPTH))
    return body.cut(cyl_x(*GATE_PT, INSERT_HOLE_D, *gx))


def build_end_gate():
    """Closes the end the speaker slides in from. Its plug sits in the end opening (so it can't
    swing), and one security screw into the back section stops it being pulled off or lifted."""
    xa, xb = sorted((gate_x_out, gate_x_out + gate_side * GATE_T))
    plate = box(xa, xb, cradle_y0, gate_y1, PLATE_T, rim_z).edges("|X").fillet(CORNER_R)
    plate = plate.cut(bend_keepout(xa - 1, xb + 1, STAND_FIT))
    plug = box(*sorted((gate_x_out, gate_x_in)), pocket_y0 + GATE_FIT, pocket_y1 - GATE_FIT, floor_z, rim_z)
    return plate.union(plug).cut(cyl_x(*GATE_PT, SCREW_CLEAR_D, xa - 1, xb + 1))


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
    return tilt(shell)


def build_rear_lid():
    lid = box(-rear_w / 2, rear_w / 2, rear_y1, rear_y1 + LID_T, rear_z0, rear_z1).edges("|Y").fillet(CORNER_R)
    for x, z in LID_PTS:
        lid = lid.cut(cyl_y(x, z, SCREW_CLEAR_D, rear_y1 - 1, rear_y1 + LID_T + 1))
    return tilt(lid)


def build_reference_speaker():
    return (
        cq.Workplane("XY")
        .box(SPK_L, SPK_D, SPK_H, centered=(True, True, False))
        .edges("|Y")
        .fillet(8)
        .translate((spk_cx, (pocket_y0 + pocket_y1) / 2, floor_z))
    )


def build_reference_stand():
    """One bent sheet: flat base plate in front, a bend, then the upright leaning at UPRIGHT_ANGLE."""
    hw0 = UPRIGHT_PROFILE[0][1]
    base = (
        box(-BASE_W / 2, BASE_W / 2, -BASE_FRONT, -bend_t, 0, PLATE_T)
        .edges("|Z")
        .edges("<Y")
        .fillet(BASE_R)
    )
    cy, cz = -bend_t, PLATE_T + BEND_R  # bend center
    a0, a1 = -90.0, LEAN  # bend sweeps from straight down to square with the upright
    r = (BEND_R + PLATE_T + 5) / math.cos(math.radians((a1 - a0) / 2))

    def ray(a):
        return cy + r * math.cos(math.radians(a)), cz + r * math.sin(math.radians(a))

    wedge = yz_prism([(cy, cz), ray(a0), ray((a0 + a1) / 2), ray(a1)], -hw0 - 1, hw0 + 1)
    bend = (
        cyl_x(cy, cz, 2 * (BEND_R + PLATE_T), -hw0 - 1, hw0 + 1)
        .cut(cyl_x(cy, cz, 2 * BEND_R, -hw0 - 1, hw0 + 1))
        .intersect(wedge)
    )
    upright = tilt(box(-hw0, hw0, 0, PLATE_T, PLATE_T + bend_t, pz(STAND_H)))
    sheet = bend.union(upright).intersect(xz_prism(upright_outline(), -BASE_FRONT, PLATE_T + BEND_R))

    oval = tilt(xz_prism(oval_sketch(), -BEND_R - PLATE_T, PLATE_T + 1))
    return base.union(sheet).cut(oval)


def check(cradle, rear, lid, gate, spk, stand):
    """Fail loudly if parts overlap, holes don't line up, the speaker isn't held, or anything reaches the tablet."""
    named = {"cradle": cradle, "rear_box": rear, "rear_lid": lid, "end_gate": gate, "speaker": spk, "stand": stand}
    for name in ("cradle", "rear_box", "rear_lid", "end_gate"):
        assert named[name].val().isValid(), f"{name} is not a valid solid"
    pairs = [("cradle", "speaker"), ("cradle", "stand"), ("rear_box", "stand"), ("rear_box", "cradle"),
             ("rear_lid", "rear_box"), ("rear_lid", "stand"), ("speaker", "stand"),
             ("end_gate", "cradle"), ("end_gate", "speaker"), ("end_gate", "stand")]
    for a, b in pairs:
        vol = named[a].intersect(named[b]).val().Volume()
        assert vol < 1e-6, f"{a} overlaps {b} by {vol:.3f} mm^3"

    def pt(x, y, z):  # plate-frame point -> world vector
        return cq.Vector(x, *to_world(y, z))

    for x, z in CLAMP_PTS:
        assert not cradle.val().isInside(pt(x, tongue_y1 - 1, z)), f"no insert hole in tongue at {x, z}"
        assert not rear.val().isInside(pt(x, rear_y0 + REAR_WALL / 2, z)), f"no clamp screw hole at {x, z}"
    for x, z in LID_PTS:
        assert not rear.val().isInside(pt(x, rear_y1 - 1, z)), f"no lid insert hole at {x, z}"
        assert not lid.val().isInside(pt(x, rear_y1 + LID_T / 2, z)), f"no lid screw hole at {x, z}"
    gy, gz = GATE_PT
    assert not cradle.val().isInside(cq.Vector(gate_x_out - gate_side, gy, gz)), "no gate insert hole"
    assert not gate.val().isInside(cq.Vector(gate_x_out + gate_side * GATE_T / 2, gy, gz)), "no gate screw hole"

    # The speaker must be held: any move past its clearance runs into a bar, the end stop, or the gate
    step = FIT + 0.5
    for desc, move, blocker in (("lifted out", (0, 0, step), cradle),
                                ("slid into the port bay", (-gate_side * step, 0, 0), cradle),
                                ("slid out past the gate", (gate_side * step, 0, 0), gate)):
        assert spk.translate(move).intersect(blocker).val().Volume() > 1, f"speaker can be {desc}"

    top = max(cradle.val().BoundingBox().zmax, gate.val().BoundingBox().zmax, floor_z + SPK_H)
    assert top < TABLET_CLEAR_Z, f"customer-side parts reach Z={top:.1f}, above the tablet edge ({TABLET_CLEAR_Z})"
    if cradle_y0 < -BASE_FRONT:
        print(f"WARNING: cradle front (Y={cradle_y0:.1f}) overhangs the base plate's front edge (Y={-BASE_FRONT:.1f})")


def main():
    OUT_DIR.mkdir(exist_ok=True)
    cradle = build_cradle()
    rear = build_rear_box()
    lid = build_rear_lid()
    gate = build_end_gate()
    spk = build_reference_speaker()
    stand = build_reference_stand()
    check(cradle, rear, lid, gate, spk, stand)

    for name, part in (("cradle", cradle), ("end_gate", gate), ("rear_box", rear), ("rear_lid", lid)):
        cq.exporters.export(part, str(OUT_DIR / f"{name}.step"))
        cq.exporters.export(part, str(OUT_DIR / f"{name}.stl"), tolerance=0.05, angularTolerance=0.1)

    asm = (
        cq.Assembly(name="kiosk_speaker_mount")
        .add(cradle, name="cradle", color=cq.Color(0.2, 0.2, 0.22))
        .add(gate, name="end_gate", color=cq.Color(0.28, 0.28, 0.3))
        .add(rear, name="rear_box", color=cq.Color(0.35, 0.35, 0.38))
        .add(lid, name="rear_lid", color=cq.Color(0.45, 0.45, 0.48))
        .add(spk, name="ref_soundcore2", color=cq.Color(0.1, 0.3, 0.7, 0.6))
        .add(stand, name="ref_stand", color=cq.Color(0.7, 0.7, 0.7, 0.6))
    )
    asm.export(str(OUT_DIR / "assembly_with_references.step"))

    cb = cradle.val().BoundingBox()
    print("Checks passed: no overlaps, screw holes line up, speaker held, clear of the tablet")
    print(f"Cradle: {cb.xlen:.1f} x {cb.ylen:.1f} mm footprint, {cb.zmax:.1f} mm tall, "
          f"{cradle.val().Volume() / 1000:.0f} cm^3; end gate adds {GATE_T:.0f} mm to the width")
    print(f"Rear box: {rear_w:.1f} x {rear_y1 + LID_T - rear_y0:.1f} x {rear_z1 - rear_z0:.1f} mm (W x D x H, with lid)")
    print(f"Upright leans {LEAN:.0f} deg toward the customer; speaker top at Z={floor_z + SPK_H:.1f} mm, "
          f"bars at Z={bar_z1:.1f} mm; tablet edge at Z={TABLET_CLEAR_Z:.1f} mm")
    print(f"Wrote files to {OUT_DIR}")


if __name__ == "__main__":
    main()
