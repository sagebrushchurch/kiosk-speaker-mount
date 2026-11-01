"""
Render shaded PNG previews of the kiosk speaker cradle into ./renders.

Run:  python render.py            (after editing parameters in kiosk_speaker_mount.py)
Renders off-screen with VTK (bundled with CadQuery); no window opens.
"""

from pathlib import Path

import cadquery as cq
import vtk

import kiosk_speaker_mount as k

RENDER_DIR = Path(__file__).parent / "renders"
SIZE = (1400, 1000)

CRADLE = (0.30, 0.31, 0.34)
GATE = (0.40, 0.41, 0.45)
REAR = (0.48, 0.49, 0.52)
LID = (0.60, 0.61, 0.64)
SPEAKER = (0.15, 0.40, 0.85)
STAND = (0.85, 0.62, 0.20)
EDGE = (0.08, 0.08, 0.10)


def shape_actors(wp, color, opacity=1.0, edges=True):
    poly = wp.val().toVtkPolyData(0.05, 0.1, normals=True)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(poly)
    surf = vtk.vtkActor()
    surf.SetMapper(mapper)
    p = surf.GetProperty()
    p.SetColor(*color)
    p.SetOpacity(opacity)
    p.SetSpecular(0.25)
    p.SetSpecularPower(30)
    actors = [surf]
    if edges and opacity > 0.9:
        fe = vtk.vtkFeatureEdges()
        fe.SetInputData(poly)
        fe.BoundaryEdgesOn()
        fe.FeatureEdgesOn()
        fe.SetFeatureAngle(35)
        fe.ManifoldEdgesOff()
        fe.NonManifoldEdgesOff()
        em = vtk.vtkPolyDataMapper()
        em.SetInputConnection(fe.GetOutputPort())
        em.ScalarVisibilityOff()
        ea = vtk.vtkActor()
        ea.SetMapper(em)
        ea.GetProperty().SetColor(*EDGE)
        ea.GetProperty().SetLineWidth(1.5)
        actors.append(ea)
    return actors


def label_actor(text):
    t = vtk.vtkTextActor()
    t.SetInput(text)
    t.GetTextProperty().SetFontSize(26)
    t.GetTextProperty().SetColor(0.15, 0.15, 0.15)
    t.SetPosition(20, SIZE[1] - 50)
    return t


def render(name, title, items, direction, ortho=False, zoom=1.15, viewup=(0, 0, 1), focus=None):
    """direction: unit-ish vector from the model toward the camera. focus: optional (x, y, z) to center on."""
    ren = vtk.vtkRenderer()
    ren.SetBackground(1, 1, 1)
    ren.SetBackground2(0.86, 0.89, 0.93)
    ren.GradientBackgroundOn()
    ren.SetUseDepthPeeling(True)
    ren.SetMaximumNumberOfPeels(8)
    for wp, color, opacity in items:
        for a in shape_actors(wp, color, opacity):
            ren.AddActor(a)
    ren.AddViewProp(label_actor(title))

    win = vtk.vtkRenderWindow()
    win.SetOffScreenRendering(True)
    win.SetSize(*SIZE)
    win.SetAlphaBitPlanes(True)
    win.SetMultiSamples(0)
    win.AddRenderer(ren)

    cam = ren.GetActiveCamera()
    # ResetCamera() below re-centers on the actors; only the direction matters here
    cam.SetFocalPoint(0, 0, 0)
    cam.SetPosition(direction[0] * 1000, direction[1] * 1000, direction[2] * 1000)
    cam.SetViewUp(*viewup)
    cam.SetParallelProjection(ortho)
    ren.ResetCamera()
    if focus is not None:
        fp, pos = cam.GetFocalPoint(), cam.GetPosition()
        shift = [focus[i] - fp[i] for i in range(3)]
        cam.SetFocalPoint(*focus)
        cam.SetPosition(*(pos[i] + shift[i] for i in range(3)))
    cam.Zoom(zoom)
    ren.ResetCameraClippingRange()
    win.Render()

    grab = vtk.vtkWindowToImageFilter()
    grab.SetInput(win)
    grab.ReadFrontBufferOff()
    grab.Update()
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(RENDER_DIR / f"{name}.png"))
    writer.SetInputConnection(grab.GetOutputPort())
    writer.Write()
    win.Finalize()
    print(f"  renders/{name}.png")


def cut_x(wp, at, remove):
    """Remove the part of `wp` on one side of the plane X=at. remove: "+" (x > at) or "-" (x < at)."""
    big = 1000.0
    lo, hi = (at, at + big) if remove == "+" else (at - big, at)
    return wp.cut(k.box(lo, hi, -big, big, -big, big))


def main():
    RENDER_DIR.mkdir(exist_ok=True)
    for old in RENDER_DIR.glob("*.png"):
        old.unlink()
    cradle = k.build_cradle()
    gate = k.build_end_gate()
    rear = k.build_rear_box()
    lid = k.build_rear_lid()
    spk = k.build_reference_speaker()
    stand = k.build_reference_stand()

    parts = [(cradle, CRADLE, 1.0), (gate, GATE, 1.0), (rear, REAR, 1.0), (lid, LID, 1.0)]
    full = parts + [(spk, SPEAKER, 0.45), (stand, STAND, 0.35)]

    # Normal into the upright, toward the staff side (the rear box and lid move along it)
    ny, nz = k.to_world(1, k.PLATE_T)
    exploded = [
        (cradle.translate((0, -60, 0)), CRADLE, 1.0),
        (gate.translate((k.gate_side * 40, -60, 0)), GATE, 1.0),
        (spk.translate((0, -60, 70)), SPEAKER, 0.45),
        (stand, STAND, 0.35),
        (rear.translate((0, 50 * ny, 50 * nz)), REAR, 1.0),
        (lid.translate((0, 90 * ny, 90 * nz)), LID, 1.0),
    ]
    # Loading: gate off, speaker partway out of the end it slides in from
    loading = [
        (cradle, CRADLE, 1.0),
        (gate.translate((k.gate_side * 120, 0, 0)), GATE, 1.0),
        (spk.translate((k.gate_side * 90, 0, 0)), SPEAKER, 0.45),
        (stand, STAND, 0.35),
    ]

    # Section views: cut away the half facing the camera so the cut face is visible
    def section(at, remove, with_speaker=True):
        items = [(cut_x(cradle, at, remove), CRADLE, 1.0), (cut_x(rear, at, remove), REAR, 1.0),
                 (cut_x(lid, at, remove), LID, 1.0), (cut_x(stand, at, remove), STAND, 1.0)]
        if with_speaker:
            items.append((cut_x(spk, at, remove), SPEAKER, 0.45))
        return items

    bay_x = (k.bay_x0 + k.bay_x1) / 2
    bay_dir = 1.0 if bay_x > 0 else -1.0
    ch_x = (k.ch_x0 + k.ch_x1) / 2
    ch_side = "+" if bay_x > 0 else "-"
    bay_focus = (bay_x, (k.pocket_y0 + k.channel_y1) / 2, k.floor_z + 20)
    rear_focus = (0, *k.to_world(k.rear_y1, (k.rear_z0 + k.rear_z1) / 2))

    print("Rendering:")
    render("01_front_with_refs", "Front-left: speaker (blue) held by two bars, on the leaning stand (orange)", full,
           (-0.8, -1.3, 0.6))
    render("02_front_bare", "Front-left: printed parts only (cradle, end gate, rear box, lid)", parts,
           (-0.8, -1.3, 0.9))
    render("03_back", "Back-right: rear box clamped to the upright (cable notches top and bottom)", full,
           (0.9, 1.3, 0.6))
    render("04_port_bay", "Port bay: end-stop fins, plugs stay connected, cables go back into the channel",
           [(cradle, CRADLE, 1.0)], (bay_dir * 0.6, -1.0, 1.2), zoom=1.5, focus=bay_focus)
    render("05_top", "Top (orthographic)", full, (0, 0, 1), ortho=True, viewup=(0, 1, 0), zoom=1.2)
    render("06_rear_open", "Rear box, lid off: splitter space, clamp screws, lid inserts",
           [(cradle, CRADLE, 1.0), (rear, REAR, 1.0), (stand, STAND, 0.35)], (0.5, 1.4, 0.5), zoom=2.0,
           focus=rear_focus)
    render("07_exploded", "Exploded: cradle, gate + speaker forward, rear box + lid back", exploded,
           (-0.9, -1.2, 0.7))
    render("08_section_clamp", "Section at X=0: tongue through the oval, clamped by the rear box", section(0, "-"),
           (-1, -0.15, 0.25), ortho=True, zoom=1.3)
    render("09_section_channel", "Section through the cable channel and the hollow back", section(ch_x, ch_side),
           (bay_dir, -0.15, 0.25), ortho=True, zoom=1.3)
    render("10_loading", "Loading: gate off, speaker slides in under the bars to the end stop", loading,
           (k.gate_side * 0.9, -1.3, 0.8))


if __name__ == "__main__":
    main()
