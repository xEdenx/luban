"""Exercise native preset composition and feature scripts in disposable repositories."""
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
PRESET = ROOT / "presets" / "team-baseline"
SPECIFY = os.environ.get("TEAM_SDLC_SPECIFY") or shutil.which("specify")
if not SPECIFY and (ROOT / ".venv" / "bin" / "specify").is_file():
    SPECIFY = str(ROOT / ".venv" / "bin" / "specify")


@unittest.skipUnless(SPECIFY, "Spec Kit 1.1.2 required; set TEAM_SDLC_SPECIFY")
class PresetLifecycleTests(unittest.TestCase):
    def run_process(self, cwd, command, expected=0):
        env = dict(os.environ, GIT_AUTHOR_NAME="Fixture", GIT_AUTHOR_EMAIL="fixture@example.invalid",
                   GIT_COMMITTER_NAME="Fixture", GIT_COMMITTER_EMAIL="fixture@example.invalid")
        result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result.stdout

    def cli(self, cwd, *args, expected=0):
        return self.run_process(cwd, [SPECIFY, *args], expected)

    def init_repo(self, temp, skills=True):
        repo = temp / "business"
        options = "--commands-dir .agent-entry" + (" --skills" if skills else "")
        self.cli(temp, "init", str(repo), "--integration", "generic",
                 "--integration-options=" + options, "--script", "py", "--non-interactive")
        return repo

    def generate(self, repo, number):
        scripts = repo / ".specify" / "scripts" / "python"
        feature = json.loads(self.run_process(repo, [sys.executable, str(scripts / "create_new_feature.py"),
                              "--json", "--number", str(number), "--short-name", "fixture", "Fictional feature"]))
        plan = json.loads(self.run_process(repo, [sys.executable, str(scripts / "setup_plan.py"), "--json"]))
        return Path(feature["SPEC_FILE"]), Path(plan["IMPL_PLAN"])

    def test_native_append_generation_and_remove_preserve_project_files(self):
        for skills in (True, False):
            with self.subTest(skills=skills), tempfile.TemporaryDirectory() as temp:
                repo = self.init_repo(Path(temp).resolve(), skills)
                history = repo / "specs" / "000-history" / "spec.md"
                history.parent.mkdir(parents=True)
                history.write_text("Historical evidence", encoding="utf-8")
                playbook = repo / "docs" / "playbook.md"
                playbook.parent.mkdir()
                playbook.write_text("Fictional internal project rule", encoding="utf-8")
                protected = [history, playbook] + [p for parent in (repo / ".agent-entry", repo / ".specify" / "templates",
                             repo / ".specify" / "memory") for p in parent.rglob("*") if p.is_file()]
                fingerprints = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
                self.cli(repo, "preset", "add", "--dev", str(PRESET))
                info = json.loads(self.cli(repo, "preset", "info", "team-baseline", "--json"))
                self.assertEqual(info["version"], "0.1.0")
                self.assertEqual(info["commands"], [])
                spec, plan = self.generate(repo, 1)
                spec_text, plan_text = spec.read_text(), plan.read_text()
                self.assertIn("## User Scenarios & Testing", spec_text)
                self.assertIn("## 工作说明（团队增量记录）", spec_text)
                self.assertIn("## Constitution Check", plan_text)
                self.assertIn("## 团队约束符合性与接力", plan_text)
                self.assertEqual(fingerprints, {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in protected})
                self.cli(repo, "preset", "remove", "team-baseline")
                self.assertFalse((repo / ".specify" / "presets" / "team-baseline").exists())
                new_spec, new_plan = self.generate(repo, 2)
                self.assertNotIn("## 工作说明（团队增量记录）", new_spec.read_text())
                self.assertNotIn("## 团队约束符合性与接力", new_plan.read_text())
                self.assertEqual(spec.read_text(), spec_text)
                self.assertEqual(plan.read_text(), plan_text)
                self.assertEqual(fingerprints, {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in protected})

    def test_project_override_wins_and_invalid_manifest_fails_generation(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = self.init_repo(Path(temp).resolve())
            self.cli(repo, "preset", "add", "--dev", str(PRESET))
            override = repo / ".specify" / "templates" / "overrides" / "spec-template.md"
            override.parent.mkdir()
            override.write_text("# Project-owned specification\n", encoding="utf-8")
            spec, _ = self.generate(repo, 1)
            self.assertEqual(spec.read_text(), override.read_text())
            override.unlink()  # Remove only this test's disposable override.
            manifest = repo / ".specify" / "presets" / "team-baseline" / "preset.yml"
            manifest.write_text(manifest.read_text().replace('strategy: "append"', 'strategy: "invalid"'))
            script = repo / ".specify" / "scripts" / "python" / "create_new_feature.py"
            self.run_process(repo, [sys.executable, str(script), "--number", "2", "--short-name", "invalid",
                                   "Fictional invalid preset"], expected=1)
            self.assertFalse((repo / "specs" / "002-invalid" / "spec.md").exists())


if __name__ == "__main__":
    unittest.main()
