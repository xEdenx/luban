#!/usr/bin/env python3
"""Compatibility entry for the verifier shipped by the native Extension."""
from pathlib import Path
import runpy


if __name__ == "__main__":
    runpy.run_path(
        str(Path(__file__).resolve().parents[1] / "extensions" / "team-sdlc" / "scripts" / "verify_maven_acceptance.py"),
        run_name="__main__",
    )
