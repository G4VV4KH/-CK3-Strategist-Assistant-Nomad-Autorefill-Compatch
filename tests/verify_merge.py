"""Verify that the military window is the clean union of the two parents' edits."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile


GUI = Path("gui/window_military.gui")
PATCH = Path(__file__).resolve().parents[1]


def verify(vanilla, strategist, nomad):
    inputs = {"strategist": strategist, "vanilla": vanilla, "nomad": nomad}
    files = {name: (root / GUI).read_bytes() for name, root in inputs.items()}
    files["compatch"] = (PATCH / GUI).read_bytes()

    # Descriptors and preview images are per mod. Other shared files need review.
    def game_paths(root):
        return {
            path.relative_to(root).as_posix().casefold()
            for path in root.rglob("*")
            if path.is_file()
        } - {"descriptor.mod", "thumbnail.png"}

    overlap = game_paths(strategist) & game_paths(nomad)
    if overlap != {GUI.as_posix()}:
        raise ValueError(f"Review the set of shared game paths: {sorted(overlap)}")

    with tempfile.TemporaryDirectory() as directory:
        for name in inputs:
            # Published SA uses LF; vanilla and NA use CRLF. Keep the UTF-8 BOM.
            (Path(directory) / name).write_bytes(files[name].replace(b"\r\n", b"\n"))
        merged = subprocess.run(
            ["git", "merge-file", "--stdout", "strategist", "vanilla", "nomad"],
            cwd=directory, capture_output=True,
        )
    if merged.returncode:
        detail = merged.stderr.decode(errors="replace").strip()
        raise ValueError(f"Three-way merge needs review (exit {merged.returncode}). {detail}")
    if files["compatch"].replace(b"\r\n", b"\n") != merged.stdout:
        raise ValueError("The shipped window differs from the clean three-way merge.")
    return {
        "result": "PASS",
        "game_path_overlap": sorted(overlap),
        "three_way_merge_exact_after_eol_normalization": True,
        "input_roots": {name: str(root.resolve()) for name, root in inputs.items()},
        "gui_sha256": {name: hashlib.sha256(data).hexdigest() for name, data in files.items()},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vanilla", required=True, type=Path, help="CK3 game directory")
    parser.add_argument("--strategist", required=True, type=Path, help="Strategist release runtime")
    parser.add_argument("--nomad", required=True, type=Path, help="Nomad release runtime")
    args = parser.parse_args()
    print(json.dumps(verify(args.vanilla, args.strategist, args.nomad), indent=2))
