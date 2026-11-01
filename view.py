"""
Live 3D view in VS Code via the OCP CAD Viewer extension (bernhard-42.ocp-cad-viewer).

1. Open the viewer: Command Palette -> "OCP CAD Viewer: Open viewer" (or the OCP icon in the sidebar).
2. Run this file (F5 / "Run Python File"). Re-run after changing parameters in
   kiosk_speaker_mount.py; the viewer updates in place and keeps the camera.
"""

import sys

from ocp_vscode import Camera, get_port, set_defaults, show

import kiosk_speaker_mount as k

if get_port() is None:
    sys.exit("OCP CAD Viewer is not running. Open it first: Command Palette -> "
             "'OCP CAD Viewer: Open viewer', then run this file again.")

set_defaults(reset_camera=Camera.KEEP, axes=False, grid=(True, False, False))

show(
    k.build_cradle(),
    k.build_end_gate(),
    k.build_rear_box(),
    k.build_rear_lid(),
    k.build_reference_speaker(),
    k.build_reference_stand(),
    names=["cradle", "end_gate", "rear_box", "rear_lid", "ref_soundcore2", "ref_stand"],
    colors=["#4d4f57", "#666873", "#7a7c84", "#9a9ca3", "#2666d9", "#d99e33"],
    alphas=[1.0, 1.0, 1.0, 1.0, 0.45, 0.35],
)
