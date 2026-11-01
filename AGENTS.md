# AGENTS.md: kiosk-speaker-mount

These are instructions for AI coding agents working in this repo. Read [SESSION_NOTES.md](SESSION_NOTES.md) for the design history, decisions, and open items before you change anything.

## What this is
A parametric CadQuery model of a 3D-printable **clamp-on speaker cradle**. It has three printed parts: the cradle, a rear box, and the rear box's lid. It joins two products on a counter:
- the **AboveTEK anti-theft countertop tablet stand** (Amazon B08HRT9XDD). It is one bent steel sheet: a flat base plate runs forward under the tablet and curves up at its back edge into a tapered upright with an oval cutout. It has no round pole.
- an **Anker Soundcore 2** Bluetooth speaker (A3105)

The cradle rests on the base plate in front of the upright, below the tablet, with the grille facing the customer. A tongue on its back passes through the oval and is screwed (M3 security Torx into heat-set inserts) to the rear box on the staff side, clamping the steel between them. The speaker's USB and AUX cables **stay plugged in**. They run from an enclosed port bay, through a channel behind the speaker, and through the tongue into the rear box, which also holds a USB splitter. **One** charging cable leaves the rear box. The output is STEP files for **Onshape** and STL files for printing.

## Layout
- `kiosk_speaker_mount.py`: **the single source of truth.** It holds all parameters (top of file), the derived values, the `build_*()` functions, `check()`, and `main()`, which runs `check()` and then exports to `output/`.
- `render.py`: off-screen VTK renders to `renders/*.png`. It imports `kiosk_speaker_mount as k` and uses its derived values (`k.W`, `k.bay_x0`, `k.rear_y1`, …). It deletes the old PNGs before rendering.
- `view.py`: live view in the VS Code OCP CAD Viewer (`ocp_vscode`).
- `output/`: generated STEP/STL files. **Committed** so they can be imported into Onshape straight from GitHub.
- `renders/`: generated PNGs. **Committed** because the README shows them.

## Environment
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python kiosk_speaker_mount.py && .venv/bin/python render.py
```
Python 3.14 with CadQuery 2.8 works. VTK ships with CadQuery, so rendering needs no extra installs. `.venv/` is gitignored.

## Conventions
- **Units are mm. Axes:** X runs side to side, with 0 at the center of the oval cutout. Y runs front to back, with 0 at the upright's front face; the cradle is at negative Y (customer side) and the rear box at positive Y (staff side). Z is up, with the counter at Z=0.
- `PORT_END` is the end that has the USB/AUX flap **as seen facing the speaker grille**.
- Keep everything parametric. Add new dimensions as named UPPER_CASE constants in the parameter block, with a short comment. Put derived values in the `# derived` block. No magic numbers inside the `build_*()` functions.
- Use the helpers for axis-aligned shapes: `box(x0, x1, y0, y1, z0, z1)`, `cyl(x, y, d, z0, z1)` (along Z), `cyl_x`, `cyl_y`, `xz_prism(sketch, y0, y1)`, and `yz_prism(pts, x0, x1)`. `upright_outline()` and `oval_sketch(inset)` give the stand's profiles.
- Design for FDM printing **with no supports**: 3 mm walls, bridges no longer than about 50 mm, and 45° overhangs. The cradle prints upright on its floor, the rear box prints on its front wall, and the lid prints flat.
- Every part must stay below `TABLET_CLEAR_Z`.
- Reference bodies (`build_reference_speaker`, `build_reference_stand`) are for checking fit only. They're never printed.

## After any geometry change
1. Run `python kiosk_speaker_mount.py`. `main()` calls `check()`, which asserts the following, so a failed check stops the export:
   - Each part is a valid solid.
   - No pair of parts or references overlaps.
   - Every `CLAMP_PTS` and `LID_PTS` location has an insert hole and a matching screw hole.
   - Everything is below `TABLET_CLEAR_Z`.

   It also warns if the cradle overhangs the base plate's front edge. If you add a part or a hole pattern, extend `check()`.
2. Run `python render.py` and look at the PNGs, especially the section views `08_section_clamp` and `09_section_channel`. Optionally run `python view.py` for the live viewer.
3. Update the README (features, measurements, printing, hardware, assembly) and `SESSION_NOTES.md` if behavior or dimensions changed.
4. Commit `output/` and `renders/` together with the source. Rebuilding rewrites the timestamps in the STEP files even when the geometry is unchanged.

## Owner preferences
- **Present a plan and wait for explicit approval before writing code**, even for small changes.
- Read the current file contents before editing.
- Keep READMEs up to date in the same change set.
- The repo is `sagebrushchurch/kiosk-speaker-mount` (private). Branch: `main`.
