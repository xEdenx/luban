"""Native installation lifecycle tests; no model, network or Maven execution."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXTENSION = ROOT / "extensions" / "team-sdlc"
SPECIFY = os.environ.get("TEAM_SDLC_SPECIFY") or shutil.which("specify")
if not SPECIFY and (ROOT / ".venv" / "bin" / "specify").is_file():
    SPECIFY = str(ROOT / ".venv" / "bin" / "specify")


@unittest.skipUnless(SPECIFY, "Spec Kit 1.1.2 not installed; set TEAM_SDLC_SPECIFY to run lifecycle checks")
class ExtensionLifecycleTests(unittest.TestCase):
    def run_cli(self, cwd, *args, expected=0):
        env = dict(os.environ, GIT_AUTHOR_NAME="Fixture", GIT_AUTHOR_EMAIL="fixture@example.invalid",
                   GIT_COMMITTER_NAME="Fixture", GIT_COMMITTER_EMAIL="fixture@example.invalid")
        result = subprocess.run([SPECIFY, *args], cwd=cwd, env=env, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result.stdout

    def test_native_skills_and_commands_install_remove_preserve_existing_files(self):
        for skills in (True, False):
            with self.subTest(skills=skills), tempfile.TemporaryDirectory() as temp:
                repo = Path(temp).resolve() / "business"
                options = "--commands-dir .agent-entry" + (" --skills" if skills else "")
                self.run_cli(Path(temp), "init", str(repo), "--integration", "generic",
                             "--integration-options=" + options, "--script", "py", "--non-interactive")
                history = repo / "specs" / "001-historical" / "spec.md"
                history.parent.mkdir(parents=True)
                history.write_text("historical spec - preserve", encoding="utf-8")
                existing = list((repo / ".agent-entry").rglob("*")) + [history, repo / ".specify" / "memory" / "constitution.md"]
                fingerprints = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in existing if p.is_file()}
                self.run_cli(repo, "extension", "add", str(EXTENSION), "--dev")
                info = json.loads(self.run_cli(repo, "extension", "info", "team-sdlc", "--json"))
                self.assertEqual(len(info["commands"]), 5)
                self.assertEqual(len(info["scripts"]), 1)
                for mode in ("start", "l0", "l1", "l2", "l3"):
                    entry = (repo / ".agent-entry" / ("speckit-team-sdlc-" + mode) / "SKILL.md"
                             if skills else repo / ".agent-entry" / ("speckit.team-sdlc." + mode + ".md"))
                    self.assertTrue(entry.is_file(), entry)
                installed = repo / ".specify" / "extensions" / "team-sdlc"
                for rel in ("references/flow.md", "references/acceptance.md", "scripts/verify_maven_acceptance.py"):
                    self.assertEqual((installed / rel).read_bytes(), (EXTENSION / rel).read_bytes())
                self.assertEqual(fingerprints, {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in fingerprints})
                # Force removes only this extension in a disposable test repository.
                self.run_cli(repo, "extension", "remove", "team-sdlc", "--force")
                self.assertFalse(installed.exists())
                self.assertFalse(list((repo / ".agent-entry").glob("*team-sdlc*")))
                self.assertEqual(fingerprints, {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in fingerprints})

    def test_packaged_verifier_runs_without_standard_repository(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp).resolve()
            repo = temp / "business"
            self.run_cli(temp, "init", str(repo), "--integration", "generic",
                         "--integration-options=--commands-dir .agent-entry --skills", "--script", "py", "--non-interactive")
            self.run_cli(repo, "extension", "add", str(EXTENSION), "--dev")
            for filename in ("spec.md", "acceptance.json"):
                shutil.copyfile(ROOT / "examples" / "maven-acceptance" / filename, repo / filename)
            reports = repo / "target" / "surefire-reports"
            reports.mkdir(parents=True)
            shutil.copyfile(ROOT / "examples" / "maven-acceptance" / "fixtures" / "TEST-example.OrderTimeoutTest.xml",
                            reports / "TEST-example.OrderTimeoutTest.xml")
            verifier = repo / ".specify" / "extensions" / "team-sdlc" / "scripts" / "verify_maven_acceptance.py"
            result = subprocess.run([sys.executable, str(verifier), "--repo", str(repo), "--mapping", "acceptance.json",
                                     "--reports-only"], cwd=temp, capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data["automated_status"], "passed")
            self.assertEqual(data["delivery_status"], "requires_review")
            self.assertEqual(data["freshness"], "unverified")


if __name__ == "__main__":
    unittest.main()
