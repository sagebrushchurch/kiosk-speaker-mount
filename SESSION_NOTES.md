# Session Notes

Design history, decisions, and open items for the kiosk speaker cradle (originally a plinth). Newest entries go at the top of **History**.

## Current status (2026-11-01)
- **Redesigned** from a full-under-stand plinth to a clamp-on **cradle + rear box + lid**. The model is complete with **placeholder dimensions** scaled from product photos and the owner's photos. Nothing has been measured or test-printed yet.
- `main()` now runs `check()` automatically: valid solids, no overlaps, screw holes aligned, and everything below the tablet.
- Outputs (STEP/STL) and renders are regenerated.
- Preview tooling works: `render.py` produces PNGs, and `view.py` with the OCP CAD Viewer gives a live 3D view.

## Next steps
1. **Measure the real parts** and update the parameters in `kiosk_speaker_mount.py`:
   - Stand: sheet thickness `PLATE_T`, oval width and heights (`OVAL_W`, `OVAL_Z0/Z1`), upright widths (`UPRIGHT_PROFILE`), bend radius `BEND_R`, base depth in front of the upright `BASE_FRONT`, and base width `BASE_W`.
   - **Whether the upright leans or curves** between about Z 30 and 65 mm. The model assumes it's vertical; this is the biggest unmeasured risk for the clamp.
   - `TABLET_CLEAR_Z`: counter to the tablet's lowest edge. The owner estimated about 3 in (76 mm).
   - Speaker: length, depth, and height (`SPK_L/D/H`). The current values come from the listing: 165 × 45 × 54 mm.
   - Plug lengths of the right-angle Micro-USB and AUX cables, which set `PORT_BAY` (currently 32 mm).
   - USB splitter size (`SPLITTER_L/W/H`, currently 60 × 30 × 20 mm).
2. Regenerate, render, and review with the owner.
3. Test-print. A small test piece of only the tongue and clamp wall would check the oval fit before the full cradle print.
4. Possible refinements (each needs a plan and approval first): an `UPRIGHT_LEAN` parameter; an end stop so the speaker can't slide into the port bay (it can currently move up to about 32 mm minus the plug length); a lockable speaker retainer; hollowing the solid back section of the cradle to save plastic (the cradle is about 310 cm³).

## Key decisions
| Decision | Why |
|---|---|
| ~~Base plinth under the stand~~ (superseded 2026-11-01) | It was 219 mm deep, because the whole stand base sat in a recess, and it was held only by gravity. The owner wanted the speaker right up against the stand. |
| **Cradle on the base plate, in front of the upright**, speaker across the width | Keeps the speaker on the customer side, below the tablet, with the grille facing the customer and a compact footprint (206 × 80 mm). |
| **Clamp through the oval cutout** with a rear box on the staff side | The stand just sits on the counter (not fastened), so the mount has to hold onto the steel itself. The oval captures the tongue, and the screws pull both parts onto the plate. |
| **Security Torx (pin-in-star) M3 screws** into heat-set inserts | The owner requires that the parts can't be separated easily. The screw heads are inside the rear box, under the lid. Bolting through the base plate's front holes was offered and declined. |
| **Top open, buttons exposed** | The owner needs access to the speaker's top buttons. The speaker sits 20 mm deep and the front lip is only 8 mm, so the grille stays exposed. |
| **Cables stay plugged in**: port bay → channel behind the speaker → through the tongue → rear box | The owner wants the USB and AUX cables connected permanently. The cable path is enclosed so it's hidden from the customer. |
| One input cable, with a splitter hidden in the rear box | The owner's requirement: a single charging cable for both the tablet and the speaker. |
| Every part stays below `TABLET_CLEAR_Z` | The tablet hangs about 3 in (76 mm) above the counter at its lowest edge. |
| No supports: 45° chamfer under the cradle's back clears the bend | The bend in the steel needs clearance under the cradle; a chamfer prints cleanly where a matching fillet would need supports. |
| CadQuery script → STEP | Parametric and version-controlled, and STEP imports cleanly into Onshape. |

## Environment notes
- Python 3.14 (system) worked with `cadquery 2.8.0`, `ocp_vscode 4.2.0`, and VTK 9.6 (bundled with CadQuery).
- The VS Code extension `bernhard-42.ocp-cad-viewer` v4.2.0 is installed on the owner's machine.
- `view.py` checks `ocp_vscode.get_port()` first, because `ocp_vscode` only *prints* connection errors and doesn't raise them, and `set_defaults()` also contacts the viewer.
- `render.py` section views cut away the half nearest the camera; an earlier bug kept the wrong half.
- Rebuilding rewrites the timestamps inside the STEP files even when the geometry hasn't changed.

## History
### 2026-11-01: Redesign to a clamp-on cradle
- The owner asked why the plinth was so deep (219 mm) and wanted the speaker right up against the stand. They also pointed out that the stand just sits on the counter, so the plinth wasn't attached to anything.
- From the owner's photos, the speaker goes on the **front (customer side), below the tablet**, which hangs about 3 in above the counter. The photos also show the stand is **one bent steel sheet**: the base runs forward under the tablet and curves up into the upright, with nothing behind the upright. The oval continues into the base as a narrow slot, and there are 4 countersunk counter-screw holes and rubber feet underneath.
- Replaced the plinth and bottom cover with a **cradle** on the base plate, a **tongue** through the oval, a **rear box** clamped on with M3 security Torx screws, and a **lid**. The owner approved this plan, including security Torx, and declined optional bolts through the base plate.
- The reference stand is now the bent sheet (`build_reference_stand`). `BASE_T` was merged into `PLATE_T`, `BASE_D` was removed, and `BASE_FRONT` was set to 150 mm.
- Added `check()` to `main()`, so overlap and hole-alignment checks run on every build. Confirmed they're meaningful: shifting a part by 1 mm makes them fail.
- Deepened the cradle's back section (`spine_d` = 29 mm, footprint 206 × 80 mm), so the strap grooves under the pocket floor end clear of the bend.
- New renders: `06_rear_open`, `08_section_clamp`, `09_section_channel`. The old `06_underside`, `08_section_port_bay`, and `09_section_center` were removed.

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
