"""
Render shaded PNG previews of the kiosk speaker plinth into ./renders.

Run:  python render.py            (after editing parameters in kiosk_speaker_mount.py)
Renders off-screen with VTK (bundled with CadQuery); no window opens.
"""

from pathlib import Path

import cadquery as cq
import vtk

import kiosk_speaker_mount as k

RENDER_DIR = Path(__file__).parent / "renders"
SIZE = (1400, 1000)

PLINTH = (0.30, 0.31, 0.34)
COVER = (0.48, 0.49, 0.52)
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
    cx, cy, cz = 0.0, k.D / 2, k.H / 2
    cam.SetFocalPoint(cx, cy, cz)
    cam.SetPosition(cx + direction[0] * 1000, cy + direction[1] * 1000, cz + direction[2] * 1000)
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
    plinth = k.build_plinth()
    cover = k.build_cover()
    spk = k.build_reference_speaker()
    stand = k.build_reference_stand_base()

    full = [(plinth, PLINTH, 1.0), (cover, COVER, 1.0), (spk, SPEAKER, 0.45), (stand, STAND, 0.35)]
    bare = [(plinth, PLINTH, 1.0), (cover, COVER, 1.0)]

    lift = 70.0
    exploded = [
        (plinth, PLINTH, 1.0),
        (cover.translate((0, 0, -lift)), COVER, 1.0),
        (spk.translate((0, 0, lift)), SPEAKER, 0.45),
        (stand.translate((0, 0, lift * 1.4)), STAND, 0.35),
    ]

    # Section views: cut away the half facing the camera so the cut face is visible
    bay_x = (k.bay_x0 + k.bay_x1) / 2
    bay_side = "+" if bay_x > 0 else "-"
    other_side = "-" if bay_side == "+" else "+"
    bay_dir = 1.0 if bay_side == "+" else -1.0
    sect_bay = [(cut_x(plinth, bay_x, bay_side), PLINTH, 1.0),
                (cut_x(cover, bay_x, bay_side), COVER, 1.0)]
    sect_mid = [(cut_x(plinth, k.spk_cx, other_side), PLINTH, 1.0),
                (cut_x(cover, k.spk_cx, other_side), COVER, 1.0),
                (cut_x(spk, k.spk_cx, other_side), SPEAKER, 0.45)]
    bay_focus = (bay_x, (k.pocket_y0 + k.pocket_y1) / 2, k.H * 0.6)

    print("Rendering:")
    render("01_front_with_refs", "Front-left: speaker (blue) + stand base (orange) references", full, (-0.8, -1.3, 0.9))
    render("02_front_bare", "Front-left: plinth + cover only", bare, (-0.8, -1.3, 0.9))
    render("03_back", "Back-right: tablet cable notch (top), input cable notch (bottom)", bare, (0.9, 1.3, 0.8))
    render("04_port_bay", "Port bay close-up: open floor drops connected cables into cavity", bare,
           (bay_dir * 0.6, -1.0, 1.2), zoom=2.2, focus=bay_focus)
    render("05_top", "Top (orthographic)", full, (0, 0, 1), ortho=True, viewup=(0, 1, 0), zoom=1.2)
    render("06_underside", "Underside, cover removed: ribs, bosses, cable cavity", [(plinth, PLINTH, 1.0)],
           (-0.7, -1.0, -1.3), zoom=0.95)
    render("07_exploded", "Exploded: stand base, speaker, plinth, cover", exploded, (-0.8, -1.3, 0.7), zoom=1.2)
    render("08_section_port_bay", "Section through port bay (cable path into cavity)", sect_bay,
           (bay_dir, -0.25, 0.3), ortho=True, zoom=1.3)
    render("09_section_center", "Section through speaker center (cradle depth, ribs, cavity)", sect_mid,
           (-bay_dir, -0.25, 0.3), ortho=True, zoom=1.3)


if __name__ == "__main__":
    main()
