"""Synthetic acceptance contracts and temporary Git repositories; no Maven invocation."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "extensions" / "team-sdlc" / "scripts" / "verify_maven_acceptance.py"
LOADER = importlib.util.spec_from_file_location("verifier", SCRIPT)
V = importlib.util.module_from_spec(LOADER)
LOADER.loader.exec_module(V)
XML = '<testsuite><testcase classname="example.Test" name="works"/></testsuite>'


class AcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.spec = self.repo / "spec.md"
        self.spec.write_text('1. **AC-001**: Given X, When Y, Then Z.\n', encoding="utf-8")
        self.mapping = self.repo / "acceptance.json"
        self.data = {"schema_version": "0.1", "change_id": "synthetic", "risk_level": "L1",
                     "spec": "spec.md", "report_sets": [{"module": ".", "kind": "surefire"}],
                     "criteria": [{"id": "AC-001", "kind": "automated", "tests": [
                         {"module": ".", "kind": "surefire", "class": "example.Test", "name": "works"}]}]}
        self.save()

    def save(self):
        self.mapping.write_text(json.dumps(self.data), encoding="utf-8")

    def report(self, xml=XML, module=".", kind="surefire", filename="TEST-example.Test.xml"):
        path = self.repo / module / "target" / (kind + "-reports") / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(xml, encoding="utf-8")
        return path

    def diagnostic(self):
        data, _ = V.load_contract(self.repo, self.mapping)
        return V.inspect_reports(self.repo, data, V.report_files(self.repo, data))

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), *args], check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout.strip()

    def commit(self):
        self.git("init", "-q")
        (self.repo / ".gitignore").write_text("target/\nlocal-results/\n", encoding="utf-8")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "synthetic baseline")
        return self.git("rev-parse", "HEAD")

    def cli(self, code=None, extra=()):
        command = [sys.executable, str(SCRIPT), "--repo", str(self.repo),
                   "--mapping", "acceptance.json", *extra]
        if code is None:
            command += ["--reports-only"]
        else:
            command += ["--output", str(self.root / "result.json"), "--", sys.executable, "-c", code]
        result = subprocess.run(command, capture_output=True, text=True, timeout=15)
        return result.returncode, json.loads(result.stdout)

    def writer(self, suffix=""):
        return ("from pathlib import Path; p=Path('target/surefire-reports/TEST-example.Test.xml'); "
                "p.parent.mkdir(parents=True,exist_ok=True); p.write_text(" + repr(XML) + "); " + suffix)

    def test_reports_only_never_claims_delivery_or_freshness(self):
        self.report()
        code, result = self.cli()
        self.assertEqual(code, 0)
        self.assertEqual(result["automated_status"], "passed")
        self.assertEqual(result["delivery_status"], "requires_review")
        self.assertEqual(result["freshness"], "unverified")
        self.assertIsNone(result["execution"])

    def test_ac_missing_extra_duplicate_and_zero(self):
        for text in ('', '1. **AC-002**: X', '1. **AC-001**: X\n2. **AC-001**: Y',
                     '1. **AC-001**: X\n2. **AC-002**: Y'):
            with self.subTest(text=text):
                self.spec.write_text(text, encoding="utf-8")
                with self.assertRaises(V.ContractError):
                    V.load_contract(self.repo, self.mapping)

    def test_fenced_example_is_not_an_ac(self):
        self.spec.write_text('```markdown\n1. **AC-999**: example\n```\n1. **AC-001**: real\n', encoding="utf-8")
        self.assertEqual(V.ac_ids(self.spec), {"AC-001"})

    def test_duplicate_json_keys_rejected(self):
        self.mapping.write_text('{"schema_version":"0.1","schema_version":"0.1"}', encoding="utf-8")
        with self.assertRaisesRegex(V.ContractError, "Duplicate JSON"):
            V.load_contract(self.repo, self.mapping)

    def test_duplicate_mapped_ac_and_unknown_selector_rejected(self):
        original = json.loads(json.dumps(self.data))
        self.data["criteria"].append(self.data["criteria"][0])
        self.save()
        with self.assertRaises(V.ContractError):
            V.load_contract(self.repo, self.mapping)
        self.data = original
        self.data["criteria"][0]["tests"][0]["module"] = "unknown"
        self.save()
        with self.assertRaises(V.ContractError):
            V.load_contract(self.repo, self.mapping)

    def test_missing_and_zero_reports_fail(self):
        self.assertTrue(self.diagnostic()[0])
        self.report('<testsuite tests="0"/>')
        self.assertTrue(self.diagnostic()[0])

    def test_skipped_failed_error_and_flaky_required_tests_fail(self):
        for tag in ("skipped", "failure", "error", "flakyFailure", "flakyError", "rerunFailure", "rerunError"):
            with self.subTest(tag=tag):
                self.report('<testsuite><testcase classname="example.Test" name="works"><' + tag + '/></testcase></testsuite>')
                self.assertTrue(self.diagnostic()[0])
                self.assertEqual(self.diagnostic()[2][0]["status"], "failed")

    def test_failure_outside_mapped_ac_still_fails(self):
        self.report(XML.replace('</testsuite>', '<testcase classname="Other" name="broken"><failure/></testcase></testsuite>'))
        self.assertTrue(self.diagnostic()[0])

    def test_unmapped_skipped_is_visible(self):
        self.report(XML.replace('</testsuite>', '<testcase classname="Other" name="skip"><skipped/></testcase></testsuite>'))
        issues, _, _, counts = self.diagnostic()
        self.assertFalse(issues)
        self.assertEqual(counts["skipped"], 1)

    def test_duplicate_testcase_is_ambiguous(self):
        self.report(XML.replace('</testsuite>', '<testcase classname="example.Test" name="works"/></testsuite>'))
        self.assertTrue(self.diagnostic()[0])

    def test_malformed_xml_and_entity_declaration_fail(self):
        for xml in ('<testsuite>', '<!DOCTYPE testsuite [<!ENTITY x "a">]>' + XML):
            with self.subTest(xml=xml):
                self.report(xml)
                self.assertTrue(self.diagnostic()[0])

    def test_multimodule_and_failsafe_match_exact_identity(self):
        (self.repo / "service").mkdir()
        self.data["report_sets"].append({"module": "service", "kind": "failsafe"})
        self.data["criteria"][0]["tests"].append({"module": "service", "kind": "failsafe", "class": "example.Test", "name": "works"})
        self.save()
        self.report()
        self.report(module="service", kind="failsafe")
        self.assertFalse(self.diagnostic()[0])
        self.report('<testsuite><testcase classname="example.Test" name="different"/></testsuite>', module="service", kind="failsafe")
        self.assertTrue(self.diagnostic()[0])

    def test_manual_ac_remains_unverified(self):
        self.data["criteria"] = [{"id": "AC-001", "kind": "manual", "reason": "human judgment", "procedure": "review"}]
        self.data["report_sets"] = []
        self.save()
        code, result = self.cli()
        self.assertEqual(code, 0)
        self.assertEqual(result["automated_status"], "not_applicable")
        self.assertEqual(result["criteria"][0]["status"], "unverified")
        self.assertEqual(result["delivery_status"], "requires_review")

    def test_path_escape_rejected(self):
        self.data["spec"] = "../outside.md"
        self.save()
        with self.assertRaisesRegex(V.ContractError, "escapes"):
            V.load_contract(self.repo, self.mapping)

    def test_fresh_run_binds_committed_source_and_logs(self):
        head = self.commit()
        code, result = self.cli(self.writer())
        self.assertEqual(code, 0, result)
        self.assertEqual(result["execution"]["tested_commit"], head)
        self.assertEqual(result["freshness"], "checked")
        self.assertTrue((self.root / "result.json.log").exists())
        self.assertEqual(json.loads((self.root / "result.json").read_text()), result)

    def test_nonzero_command_cannot_pass_with_good_xml(self):
        self.commit()
        code, result = self.cli(self.writer("raise SystemExit(3)"))
        self.assertEqual(code, 1)
        self.assertEqual(result["delivery_status"], "not_ready")
        self.assertEqual(result["execution"]["exit_code"], 3)

    def test_old_report_and_noop_command_fail(self):
        self.report()
        self.commit()
        code, result = self.cli("pass")
        self.assertEqual(code, 1)
        self.assertEqual(result["freshness"], "failed")

    def test_source_change_during_run_fails(self):
        self.commit()
        code, result = self.cli(self.writer("Path('new-source.java').write_text('changed')"))
        self.assertEqual(code, 1)
        self.assertTrue(any("clean" in issue for issue in result["issues"]))

    def test_dirty_worktree_prevents_execution(self):
        self.commit()
        self.spec.write_text('1. **AC-001**: changed', encoding="utf-8")
        code, result = self.cli(self.writer())
        self.assertEqual(code, 2)
        self.assertIn("clean", result["error"])
        self.assertFalse((self.repo / "target").exists())

    def test_unborn_repository_prevents_execution(self):
        self.git("init", "-q")
        code, _ = self.cli(self.writer())
        self.assertEqual(code, 2)

    def test_refuses_result_overwrite(self):
        self.commit()
        (self.root / "result.json").write_text("preserve", encoding="utf-8")
        code, result = self.cli(self.writer())
        self.assertEqual(code, 2)
        self.assertIn("overwrite", result["error"])
        self.assertEqual((self.root / "result.json").read_text(), "preserve")

    def test_output_inside_repo_must_be_ignored(self):
        self.commit()
        with self.assertRaisesRegex(V.ContractError, "ignored"):
            V.output_paths(self.repo, self.repo / "evidence.json")
        output, _ = V.output_paths(self.repo, self.repo / "local-results" / "evidence.json")
        self.assertEqual(output, self.repo / "local-results" / "evidence.json")

    def test_changed_head_during_execution_fails(self):
        self.commit()
        suffix = ("import subprocess; subprocess.run(['git','-c','user.name=Fixture',"
                  "'-c','user.email=fixture@example.invalid','commit','--allow-empty','-qm','new head'],check=True)")
        code, result = self.cli(self.writer(suffix))
        self.assertEqual(code, 1)
        self.assertTrue(any("commit changed" in issue for issue in result["issues"]))

    def test_missing_executable_is_failed_evidence(self):
        self.commit()
        result = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(self.repo), "--mapping", "acceptance.json",
                                 "--output", str(self.root / "result.json"), "--", str(self.root / "nonexistent")],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 1)
        self.assertIsNone(json.loads(result.stdout)["execution"]["exit_code"])


if __name__ == "__main__":
    unittest.main()
