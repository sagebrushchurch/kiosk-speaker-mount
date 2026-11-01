# Session Notes

Design history, decisions, and open items for the kiosk speaker plinth. Newest entries go at the top of **History**.

## Current status (2026-11-01)
- The model is complete with **placeholder dimensions** taken from Amazon listings. Nothing has been measured or test-printed yet.
- Outputs (STEP/STL) and renders are generated and committed.
- Preview tooling works: `render.py` produces PNGs, and `view.py` with the OCP CAD Viewer gives a live 3D view.

## Next steps
1. **Measure the real parts** and update the parameters in `kiosk_speaker_mount.py`:
   - Stand base plate: width, depth, thickness, corner radius, and the positions of the existing screw holes (`STAND_BASE_*`, `STAND_HOLES`). The current values are scaled from the product image: 175 × 160 mm, 4 mm thick.
   - Speaker: length, depth, and height (`SPK_L/D/H`). The current values come from the listing: 165 × 45 × 54 mm, about 6.5 × 1.77 × 2.13 in.
   - Plug lengths of the right-angle Micro-USB and AUX cables, which set `PORT_BAY` (currently 32 mm).
   - ~~Which end has the USB/AUX flap~~: **confirmed 2026-11-01** as the right end when viewed from the front (grille). `PORT_END = "right"` is correct.
2. Regenerate, render, and review with the owner.
3. Test-print. Consider a short test piece, such as only the port-bay corner or a thin slice of the stand recess, to check fit before the full ~10-hour print.
4. Possible refinements the owner may want: split the plinth into two pieces for smaller printers, add a speaker strap or lock, or add a cable strain-relief clip inside the cavity.

## Key decisions
| Decision | Why |
|---|---|
| **Base plinth** instead of a pole clamp or back-mounted bracket | The owner's product image shows the stand is a curved, tapered steel plate with an oval cutout and no round pole. A plinth under the flat base is the simplest secure fit. The owner chose option A. |
| Speaker lies **in front**, across the width | The speaker (165–168 mm) is about as wide as the stand base (175 mm), so the footprint stays compact and the speaker faces the customer. |
| **Top open, buttons exposed** | The owner needs access to the speaker's top buttons. The speaker sits 20 mm deep and the front lip is only 8 mm, so the grille stays exposed. |
| **Cables stay plugged in** with an open-floor **port bay** at the flap end | The owner wants the USB and AUX cables connected permanently. The bay floor is open into the cavity so plugs and cables drop straight down. |
| One input cable, with a splitter hidden in the cavity | The owner's requirement: a single charging cable for both the tablet and the speaker. |
| Hollow body + **screw-on bottom cover** (7× M3 heat-set inserts) | Gives access to the cables later. The bosses are placed to avoid the port bay and the strap slots. |
| **Internal arch ribs**, printed right side up | Lets the part print without supports. The pointed 45° arch openings still let cables pass front to back. |
| CadQuery script → STEP | Parametric and version-controlled, and STEP imports cleanly into Onshape. |

## Environment notes
- Python 3.14 (system) worked with `cadquery 2.8.0`, `ocp_vscode 4.2.0`, and VTK 9.6 (bundled with CadQuery).
- The VS Code extension `bernhard-42.ocp-cad-viewer` v4.2.0 is installed on the owner's machine.
- `view.py` checks `ocp_vscode.get_port()` first, because `ocp_vscode` only *prints* connection errors and doesn't raise them, and `set_defaults()` also contacts the viewer.
- `render.py` section views cut away the half nearest the camera; an earlier bug kept the wrong half.

## History
### 2026-11-01: Flap side confirmed
- The owner confirmed the USB/AUX flap is on the short end that's hidden from view, on the **right when viewed from the front**. The model already used `PORT_END = "right"`, so no geometry changed.

### 2026-11-01: Initial build
- Gathered requirements: a speaker attachment for the kiosk stand that hides cables and has one charging cable.
- Researched the products. Amazon pages only partly loaded, so dimensions came from search results and owner-supplied images.
- Considered and dropped a pole clamp once the owner's image showed the stand shape.
- Built the plinth, cover, and reference bodies, then checked validity, interference, and screw-hole alignment.
- Added internal support ribs with arch cable passages (owner approved).
- Created the GitHub repo `sagebrushchurch/kiosk-speaker-mount` (private) and pushed the first commit.
- Added `render.py` (9 views, including exploded and section views), `view.py` (OCP CAD Viewer), `.vscode` settings and recommended extensions, `AGENTS.md`, and these notes.
