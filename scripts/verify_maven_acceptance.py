#!/usr/bin/env python3
"""Experimental AC/report verification; no dependencies beyond Python 3.9+."""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET


class ContractError(ValueError):
    pass


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inside(root, path):
    path = path.resolve()
    try:
        path.relative_to(root)
    except ValueError:
        raise ContractError("Path escapes repository: " + str(path))
    return path


def pairs_without_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContractError("Duplicate JSON key: " + key)
        result[key] = value
    return result


def text_field(obj, key):
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ContractError("Missing/non-string field: " + key)
    return value


def keys(obj, required, optional=()):
    if not isinstance(obj, dict):
        raise ContractError("Expected JSON object")
    if set(obj) - set(required) - set(optional) or set(required) - set(obj):
        raise ContractError("Unexpected/missing fields: " + ", ".join(sorted(obj)))


def ac_ids(spec):
    ids = []
    fence = None
    for line in spec.read_text(encoding="utf-8").splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence:
            continue
        match = re.match(r"^\s*(?:\d+[.)]|[-*+])\s+\*\*(AC-\d{3,})\*\*(?=\s|:|$)", line)
        if match:
            ids.append(match.group(1))
    if not ids or len(ids) != len(set(ids)):
        raise ContractError("Spec must declare nonempty, unique AC IDs")
    return set(ids)


def load_contract(repo, mapping):
    data = json.loads(mapping.read_text(encoding="utf-8"), object_pairs_hook=pairs_without_duplicates)
    keys(data, ("schema_version", "change_id", "risk_level", "spec", "report_sets", "criteria"))
    if data["schema_version"] != "0.1" or data["risk_level"] not in ("L0", "L1", "L2", "L3"):
        raise ContractError("Unsupported schema_version/risk_level")
    text_field(data, "change_id")
    spec = inside(repo, mapping.parent / text_field(data, "spec"))
    expected = ac_ids(spec)
    if not isinstance(data["report_sets"], list) or not isinstance(data["criteria"], list):
        raise ContractError("report_sets and criteria must be arrays")
    sets = set()
    for item in data["report_sets"]:
        keys(item, ("module", "kind"))
        module = text_field(item, "module")
        kind = text_field(item, "kind")
        module_dir = inside(repo, repo / module)
        if not module_dir.is_dir() or kind not in ("surefire", "failsafe"):
            raise ContractError("Unsupported report set")
        canonical = module_dir.relative_to(repo).as_posix()
        if module != canonical or (module, kind) in sets:
            raise ContractError("Noncanonical/duplicate module report set")
        sets.add((module, kind))
    seen = set()
    for item in data["criteria"]:
        if not isinstance(item, dict):
            raise ContractError("AC must be an object")
        kind = item.get("kind")
        if kind == "automated":
            keys(item, ("id", "kind", "tests"))
            if not isinstance(item["tests"], list) or not item["tests"]:
                raise ContractError("Automated AC must specify tests")
            selectors = set()
            for test in item["tests"]:
                keys(test, ("module", "kind", "class", "name"))
                selector = tuple(text_field(test, field) for field in ("module", "kind", "class", "name"))
                if selector[:2] not in sets or selector in selectors:
                    raise ContractError("Unknown report set/duplicate test selector")
                selectors.add(selector)
        elif kind == "manual":
            keys(item, ("id", "kind", "reason", "procedure"))
            text_field(item, "reason")
            text_field(item, "procedure")
        else:
            raise ContractError("AC kind must be automated or manual")
        identifier = text_field(item, "id")
        if identifier in seen:
            raise ContractError("Duplicate mapped AC ID")
        seen.add(identifier)
    if seen != expected:
        raise ContractError("AC mismatch; missing=" + str(sorted(expected - seen)) + "; extra=" + str(sorted(seen - expected)))
    return data, spec


def report_files(repo, data):
    result = {}
    for item in data["report_sets"]:
        base = inside(repo, repo / item["module"] / "target" / (item["kind"] + "-reports"))
        result[(item["module"], item["kind"])] = [inside(repo, p) for p in sorted(base.glob("TEST-*.xml"))]
    return result


def fingerprints(files):
    return {str(path): (path.stat().st_mtime_ns, path.stat().st_size, digest(path))
            for group in files.values() for path in group}


def inspect_reports(repo, data, files):
    issues, records = [], []
    index = defaultdict(list)
    counts = Counter()
    for (module, kind), paths in files.items():
        if not paths:
            issues.append("Missing reports: " + module + "/" + kind)
        total = 0
        for path in paths:
            try:
                if path.stat().st_size > 10 * 1024 * 1024:
                    raise ContractError("XML exceeds 10 MiB")
                raw = path.read_bytes()
                if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
                    raise ContractError("XML DTD/entity declarations are unsupported")
                tree = ET.fromstring(raw)
                if tree.tag.rsplit("}", 1)[-1] not in ("testsuite", "testsuites"):
                    raise ContractError("Unsupported XML report root")
                cases = [e for e in tree.iter() if e.tag.rsplit("}", 1)[-1] == "testcase"]
                if not cases:
                    issues.append("Zero testcase report: " + path.relative_to(repo).as_posix())
                for case in cases:
                    classname, name = case.get("classname"), case.get("name")
                    if not classname or not name:
                        raise ContractError("testcase requires classname and name")
                    tags = {c.tag.rsplit("}", 1)[-1] for c in case.iter() if c is not case}
                    failed = bool(tags & {"failure", "error", "flakyFailure", "flakyError", "rerunFailure", "rerunError"})
                    status = "failed" if failed else "skipped" if "skipped" in tags else "passed"
                    index[(module, kind, classname, name)].append(status)
                    counts[status] += 1
                    total += 1
                    if failed:
                        issues.append("Failed/unstable test: " + classname + "#" + name)
                records.append({"path": path.relative_to(repo).as_posix(), "sha256": digest(path), "testcases": len(cases)})
            except (ET.ParseError, ContractError) as exc:
                issues.append("Invalid report " + path.relative_to(repo).as_posix() + ": " + str(exc))
        if paths and not total:
            issues.append("No usable testcases: " + module + "/" + kind)
    criteria = []
    for item in data["criteria"]:
        if item["kind"] == "manual":
            criteria.append({"id": item["id"], "kind": "manual", "status": "unverified"})
            continue
        good = True
        for test in item["tests"]:
            selector = tuple(test[k] for k in ("module", "kind", "class", "name"))
            matches = index.get(selector, [])
            if matches != ["passed"]:
                good = False
                issues.append(item["id"] + ": expected one passing testcase, found " + str(matches) + " for " + str(selector))
        criteria.append({"id": item["id"], "kind": "automated", "status": "passed" if good else "failed"})
    return issues, records, criteria, dict(counts)


def git(repo, *args):
    command = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if command.returncode:
        raise ContractError("Git check failed: " + " ".join(args))
    return command.stdout.strip()


def clean_commit(repo):
    if Path(git(repo, "rev-parse", "--show-toplevel")).resolve() != repo:
        raise ContractError("--repo must be the Git repository root")
    commit = git(repo, "rev-parse", "--verify", "HEAD")
    if any(line.startswith("160000 ") for line in git(repo, "ls-files", "--stage").splitlines()):
        raise ContractError("Git submodules are unsupported in this prototype")
    if git(repo, "status", "--porcelain", "--untracked-files=all"):
        raise ContractError("Repository must have a clean tracked/untracked worktree")
    return commit


def output_paths(repo, output):
    if output is None:
        return None, None
    output = output.resolve()
    log = output.with_suffix(output.suffix + ".log")
    for path in (output, log):
        if path.exists():
            raise ContractError("Refusing to overwrite output/log: " + str(path))
        if path.is_relative_to(repo):
            relative = path.relative_to(repo).as_posix()
            if relative.startswith(".git/") or relative == ".git":
                raise ContractError("Output cannot be inside .git")
            tracked = subprocess.run(["git", "-C", str(repo), "ls-files", "--error-unmatch", relative], capture_output=True)
            ignored = subprocess.run(["git", "-C", str(repo), "check-ignore", "--quiet", "--no-index", relative], capture_output=True)
            if tracked.returncode == 0 or ignored.returncode != 0:
                raise ContractError("In-repository output/log must be ignored and untracked")
    return output, log


def verify(args):
    repo = args.repo.resolve()
    mapping = inside(repo, repo / args.mapping)
    data, spec = load_contract(repo, mapping)
    output, log = output_paths(repo, args.output)
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if args.reports_only and command:
        raise ContractError("--reports-only cannot execute a command")
    if not args.reports_only and (not command or output is None):
        raise ContractError("Run mode requires --output and an explicit command after --")
    baseline = {"mapping_sha256": digest(mapping), "spec_sha256": digest(spec)}
    issues, execution = [], None
    freshness = "unverified"
    if not args.reports_only:
        commit = clean_commit(repo)
        before = fingerprints(report_files(repo, data))
        output.parent.mkdir(parents=True, exist_ok=True)
        started = time.time_ns()
        with log.open("x", encoding="utf-8") as stream:
            try:
                run = subprocess.run(command, cwd=repo, stdout=stream, stderr=subprocess.STDOUT, timeout=args.timeout)
                returncode = run.returncode
            except (OSError, subprocess.TimeoutExpired) as exc:
                stream.write("\nExecution error: " + str(exc))
                returncode = None
        ended = time.time_ns()
        execution = {"command": command, "exit_code": returncode, "started_ns": started, "ended_ns": ended, "tested_commit": commit}
        if returncode != 0:
            issues.append("Verification command did not exit successfully")
        try:
            if clean_commit(repo) != commit:
                issues.append("Tested commit changed during execution")
        except ContractError as exc:
            issues.append(str(exc))
        if digest(mapping) != baseline["mapping_sha256"] or digest(spec) != baseline["spec_sha256"]:
            issues.append("Spec or mapping changed during execution")
        files = report_files(repo, data)
        after = fingerprints(files)
        freshness = "checked"
        for path, value in after.items():
            if before.get(path) == value or not started <= value[0] <= ended:
                freshness = "failed"
                issues.append("Stale/not-updated report: " + str(Path(path).relative_to(repo)))
    else:
        files = report_files(repo, data)
    report_issues, records, criteria, counts = inspect_reports(repo, data, files)
    issues.extend(report_issues)
    automated = any(item["kind"] == "automated" for item in data["criteria"])
    status = "failed" if issues else "passed" if automated else "not_applicable"
    result = {"schema_version": "0.1", "change_id": data["change_id"], "risk_level": data["risk_level"],
              "mode": "reports_only" if args.reports_only else "run", "automated_status": status,
              "delivery_status": "not_ready" if issues else "requires_review", "freshness": freshness,
              "inputs": baseline, "execution": execution, "reports": records, "counts": counts,
              "criteria": criteria, "issues": issues,
              "limitations": ["Local evidence is not authenticated human approval.",
                              "Only declared report sets are checked; reviewer must confirm Maven/profile coverage.",
                              "Report-only mode does not verify execution, source version or freshness."]}
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8") as stream:
            stream.write(rendered)
    print(rendered, end="")
    return 1 if issues else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--reports-only", action="store_true")
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    try:
        if args.timeout <= 0:
            raise ContractError("Timeout must be positive")
        return verify(args)
    except (ContractError, OSError, ValueError, TypeError) as exc:
        print(json.dumps({"automated_status": "failed", "delivery_status": "not_ready", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
