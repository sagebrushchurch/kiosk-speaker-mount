# Kiosk Speaker Cradle

A clamp-on speaker cradle for the AboveTEK countertop tablet stand. An Anker Soundcore 2 sits in a cradle on the front of the stand's base plate, below the tablet, with the grille facing the customer. A tongue on the back of the cradle passes through the oval cutout in the stand's upright, which leans toward the customer. It is screwed to a small rear box on the staff side with security Torx screws, so the steel plate is clamped between the two parts and they can't be separated without the driver bit.

The speaker slides in from the customer's left, under two bars that stop it being lifted out, until it reaches an end stop. A screwed end gate then closes the left end. Its USB and AUX cables stay plugged in. They run from a port bay, through a channel behind the speaker, and through the tongue into the rear box, which hides a USB splitter. One charging cable comes out of the rear box.

## Files (`output/`)
| File | Use |
|---|---|
| `cradle.step` / `.stl` | Speaker cradle with the bars, end stop, port bay, cable channel, and clamp tongue |
| `end_gate.step` / `.stl` | End gate that closes the end the speaker slides in from |
| `rear_box.step` / `.stl` | Rear box (staff side) that clamps the tongue and holds the splitter |
| `rear_lid.step` / `.stl` | Screw-on lid for the rear box |
| `assembly_with_references.step` | All four parts plus see-through reference bodies for the speaker and the stand. Use this to check fit in Onshape. |

All files are exported in their assembled position. The rear box and lid are tilted to match the upright, so lay them flat in your slicer (see [Printing](#printing)).

**Onshape:** Go to Documents → Import, choose the STEP file, and set units to millimeters. Imported parts come in as plain solids, so make changes in `kiosk_speaker_mount.py` and re-import, or edit the imported part with Onshape features.

## Regenerate
```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python kiosk_speaker_mount.py   # checks the fit, then writes output/*.step and *.stl
python render.py                # writes renders/*.png
```
All dimensions are parameters at the top of the script. Before exporting, the script checks that the parts don't overlap each other, the speaker, or the stand, that all screw holes line up, that the speaker can't be lifted or slid out, and that nothing on the customer side reaches the tablet. If any check fails, it stops with an error. The checked-in [.vscode/settings.json](.vscode/settings.json) points VS Code at `.venv`.

## Preview
**Live 3D in VS Code:** Install the **OCP CAD Viewer** extension (`bernhard-42.ocp-cad-viewer`). Open the viewer from the Command Palette with *OCP CAD Viewer: Open viewer*, then run [view.py](view.py). After you change a parameter, run `view.py` again; the view updates and keeps your camera angle.

**Static renders:** [render.py](render.py) draws PNG images into [renders/](renders) off-screen. Run it again and commit the images whenever the design changes.

| | | |
|---|---|---|
| ![front](renders/01_front_with_refs.png) | ![front bare](renders/02_front_bare.png) | ![back](renders/03_back.png) |
| ![port bay](renders/04_port_bay.png) | ![top](renders/05_top.png) | ![rear box open](renders/06_rear_open.png) |
| ![exploded](renders/07_exploded.png) | ![section clamp](renders/08_section_clamp.png) | ![section channel](renders/09_section_channel.png) |
| ![loading](renders/10_loading.png) | | |

**Measure these and update them before printing.** The stand values are currently scaled from product photos.
- `PLATE_T`: steel sheet thickness. The clamp grips this.
- `UPRIGHT_ANGLE`: the upright's angle up from the counter (currently 75°, leaning toward the customer). The clamp and the cradle's back are built to match it.
- `OVAL_W`, `OVAL_Z0/Z1`: oval cutout width, and its bottom and top heights above the counter.
- `UPRIGHT_PROFILE`: upright width at several heights.
- `BEND_R`: inside radius where the base plate curves up into the upright.
- `BASE_FRONT`, `BASE_W`: base plate depth in front of the upright, and its width.
- `TABLET_CLEAR_Z`: counter to the tablet's lowest edge (currently a 76 mm estimate). Every part on the customer side must stay below it.
- `SPK_L/D/H`: speaker length, depth, and height. They currently use the listed 165 × 45 × 54 mm.
- `BAR_X`: where the two top bars sit, measured from the speaker's center (±72 mm). Check that they miss the top buttons.
- `PORT_BAY`: room for the connected plugs. 32 mm assumes right-angle plugs; increase it for straight plugs.
- `SPLITTER_L/W/H`: size of the USB splitter that goes in the rear box.

`PORT_END` (the end with the USB/AUX flap when you face the grille) is **confirmed as `"right"`** for the Soundcore 2.

## Project files
| File | Purpose |
|---|---|
| [kiosk_speaker_mount.py](kiosk_speaker_mount.py) | Parametric model and export script |
| [render.py](render.py) | Draws the PNG previews in `renders/` |
| [view.py](view.py) | Sends the model to the OCP CAD Viewer in VS Code |
| [AGENTS.md](AGENTS.md) | Context and conventions for AI agents (Copilot loads it automatically) |
| [SESSION_NOTES.md](SESSION_NOTES.md) | Design decisions, history, and open items |

## Features
- The cradle rests on the stand's base plate, right up against the front of the upright. Its back follows the upright's 75° lean. The footprint is 206 × 80 mm, plus the 4 mm end gate. The speaker top is at 64 mm and the bars at 68.5 mm, below the tablet's estimated 76 mm edge.
- The speaker sits 20 mm deep in the cradle. The front lip is only 8 mm, so the grille stays exposed.
- **Speaker retention:**
  - Two 12 mm bars go over the ends of the speaker, so it can't be lifted out. The top buttons between them stay clear.
  - Fins at the front and back of the pocket form an end stop, so the speaker can't slide into the port bay. The plugs pass between the fins.
  - The end gate closes the left end. Its plug sits in the end opening so it can't swing, and one M3 security Torx screw into the back section holds it on.
- **Clamp:** the tongue passes through the oval and is pulled against the upright by 2 M3 security Torx screws from inside the rear box. The tongue, screws, and rear box are all square to the leaning plate. The tongue is 0.5 mm shorter than the plate thickness, so the screws squeeze both parts onto the steel. Once the lid is on, the screw heads are hidden.
- **Port bay** at the flap end, walled in up to the back height and open on top so you can reach the plugs. The plugs stay connected, and the cables go back into a 12 mm channel behind the speaker, then through a 14 × 14 mm passage in the tongue into the rear box.
- **Rear box** (84 × 30 × 42 mm with the lid) sits above the bend on the staff side. It holds the splitter. A top notch passes the tablet charging and audio cables, and a bottom notch lets the single input cable out.
- **Hollow back:** sealed cavities with 3 mm walls, cross ribs, and 45° peaked roofs take about 42 cm³ out of the cradle's back section. The cradle is about 212 cm³.
- A chamfer of at least 45° under the back of the cradle clears the bend in the steel and prints without supports.

## Hardware
- 5 × M3 heat-set inserts (4.0 mm hole, 6 mm deep): 2 in the tongue, 2 for the lid, 1 for the end gate
- 5 × M3 × 8 security Torx (pin-in-star) button-head screws (2 clamp, 2 lid, 1 end gate), plus the matching driver bit
- USB splitter or 2-port charger cable: tablet lead plus Micro-USB lead for the speaker (right-angle Micro-USB recommended)
- Right-angle 3.5 mm AUX cable

## Assembly
1. Install the heat-set inserts: 2 in the tongue, 2 in the rear box's lid bosses, and 1 in the cradle's left end (behind the speaker pocket).
2. Set the cradle on the base plate and push the tongue through the oval from the front.
3. Hold the rear box against the back of the upright and screw it to the tongue from inside the box.
4. Fit the splitter and route the cables through the tongue into the channel and the port bay.
5. Slide the speaker in from the left end, under both bars, until it stops at the fins. Plug in the cables from above the port bay.
6. Fit the end gate and screw it on, then screw on the rear box lid.

The cradle may cover the base plate's rear counter-screw holes. If the stand will be screwed to the counter, do that before fitting the cradle.

## Printing
- No supports are needed for any part. The cradle needs a bed of at least 210 mm in one direction.
- Print the **cradle** upright, standing on its floor. The bars bridge 48 mm over the pocket.
- Print the **end gate** flat, on its outer face.
- Print the **rear box** with its front (clamp) wall on the bed, and the **lid** flat. Both are exported tilted, so use your slicer's "lay on face" tool.
- PETG or PLA, 3 walls, 15–20% infill.
