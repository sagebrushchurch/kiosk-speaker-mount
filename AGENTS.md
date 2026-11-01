# AGENTS.md: kiosk-speaker-mount

These are instructions for AI coding agents working in this repo. Read [SESSION_NOTES.md](SESSION_NOTES.md) for the design history, decisions, and open items before you change anything.

## What this is
A parametric CadQuery model of a 3D-printable **plinth**, a hollow base with a bottom cover. It joins two products on a counter:
- the **AboveTEK anti-theft countertop tablet stand** (Amazon B08HRT9XDD), which is a bent steel plate stand with a flat base plate, not a round pole
- an **Anker Soundcore 2** Bluetooth speaker (A3105)

The stand's base plate drops into a recess on top. The speaker lies across a cradle at the front. Its USB and AUX cables **stay plugged in** and drop through an open-floor "port bay" into a hidden cavity, which also holds a USB splitter. **One** charging cable leaves the back. The output is STEP files for **Onshape** and STL files for printing.

## Layout
- `kiosk_speaker_mount.py`: **the single source of truth.** It holds all parameters (top of file), the `build_*()` functions, and `main()`, which exports to `output/`.
- `render.py`: off-screen VTK renders to `renders/*.png`. It imports `kiosk_speaker_mount as k` and uses its derived values (`k.W`, `k.bay_x0`, …).
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
- **Units are mm. Axes:** X runs side to side, centered on 0. Y runs front to back, with the front face at Y=0 and the speaker side at the front. Z is up, with the plinth bottom at Z=0 and the cover below Z=0.
- `PORT_END` is the end that has the USB/AUX flap **as seen facing the speaker grille**.
- Keep everything parametric. Add new dimensions as named UPPER_CASE constants in the parameter block, with a short comment. Put derived values in the `# derived` block. No magic numbers inside the `build_*()` functions.
- Use the `box(x0, x1, y0, y1, z0, z1)` and `cyl(x, y, d, z0, z1)` helpers for axis-aligned cuts.
- Design for FDM printing **right side up with no supports**: 3 mm walls, bridges no longer than about 50 mm, and 45° pointed-arch openings in ribs.
- Reference bodies (`build_reference_speaker`, `build_reference_stand_base`) are for checking fit only. They're never printed.

## After any geometry change
1. Run `python kiosk_speaker_mount.py`. It asserts that each part is a valid solid.
2. Check for interference and that holes line up. The plinth must have zero intersection volume with the speaker, the stand base, and the cover. Every `BOSS_PTS` location must have an insert hole in the plinth (Z≈3) and a screw hole in the cover (Z≈-1.5). Snippet:
   ```python
   import cadquery as cq, kiosk_speaker_mount as k
   p, c = k.build_plinth(), k.build_cover()
   for o in (k.build_reference_speaker(), k.build_reference_stand_base(), c):
       assert p.intersect(o).val().Volume() < 1e-6
   for x, y in k.BOSS_PTS:
       assert not p.val().isInside(cq.Vector(x, y, 3)) and not c.val().isInside(cq.Vector(x, y, -1.5))
   ```
3. Run `python render.py` and look at the PNGs, especially the section views `08_` and `09_`.
4. Update the README (features, printing, hardware) and `SESSION_NOTES.md` if behavior or dimensions changed.
5. Commit `output/` and `renders/` together with the source.

## Owner preferences
- **Present a plan and wait for explicit approval before writing code**, even for small changes.
- Read the current file contents before editing.
- Keep READMEs up to date in the same change set.
- The repo is `sagebrushchurch/kiosk-speaker-mount` (private). Branch: `main`.
