#!/usr/bin/env python3
"""Does each benchmark rep's final manifest carry the latest version of its
target package, and if so, how did it get there (model already knew it, a
registry/package-manager lookup, or yul's hook forcing a correction)?

Usage:
    python3 benchmark/analyze_top.py [RUN_DIR] [--yul PATH_TO_YUL_BINARY]

Requires network access (queries each ecosystem's registry for the latest
version of every target package via `yul scan`).
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from collections import Counter, defaultdict

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent


def load_cases(cases_path, top_packages_path):
    cases = json.load(open(cases_path))
    top_packages = json.load(open(top_packages_path))["ecosystems"]

    by_eco_index = {}
    for eco, data in top_packages.items():
        for idx, pkg in enumerate(data["packages"], start=1):
            by_eco_index[(eco, idx)] = pkg

    meta = {}
    for c in cases:
        cid = c["id"]
        m = re.match(r"^(pypi|maven|cargo|npm|go|ghactions)-top-(\d+)-", cid)
        if not m:
            continue
        prefix, idx = m.group(1), int(m.group(2))
        eco = "githubactions" if prefix == "ghactions" else prefix
        manifest = c["manifest"]
        if isinstance(manifest, str):
            manifest = [manifest]
        meta[cid] = {
            "ecosystem": eco,
            "package": by_eco_index.get((eco, idx)),
            "manifests": manifest,
        }
    return meta


# ---------------------------------------------------------------------------
# Per-ecosystem: does the target package appear pinned to an exact version
# in this manifest's final content, and if so what version?
# ---------------------------------------------------------------------------

def find_pin_npm(content, pkg):
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return None
    for field in ("dependencies", "devDependencies", "optionalDependencies", "peerDependencies"):
        spec = data.get(field, {}).get(pkg)
        if spec is None:
            continue
        spec = spec.strip()
        if re.fullmatch(r"\d+\.\d+\.\d+(-[0-9A-Za-z.]+)?(\+[0-9A-Za-z.]+)?", spec):
            return ("exact", spec)
        return ("range", spec)
    return None


def find_pin_pypi_requirements(content, pkg):
    for line in content.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        norm = pkg.replace("-", "[-_.]").replace("_", "[-_.]")
        m = re.match(rf"^(?:{re.escape(pkg)}|{norm})\s*(==|>=|<=|~=|!=|>|<)\s*([^\s;,]+)", line, re.IGNORECASE)
        if m:
            op, ver = m.group(1), m.group(2)
            if op == "==" and "," not in line:
                return ("exact", ver)
            return ("range", f"{op}{ver}")
    return None


def find_pin_pypi_pyproject(content, pkg):
    namere = re.escape(pkg)
    normre = pkg.replace("-", "[-_.]").replace("_", "[-_.]")
    for pat in (namere, normre):
        m = re.search(rf'"({pat})\s*(==|>=|<=|~=|!=|>|<|\^)\s*([^"\s;,]+)"', content, re.IGNORECASE)
        if m:
            op, ver = m.group(2), m.group(3)
            return ("exact", ver) if op == "==" else ("range", f"{op}{ver}")
        m = re.search(rf'^\s*({pat})\s*=\s*"([^"]+)"', content, re.IGNORECASE | re.MULTILINE)
        if m:
            spec = m.group(2).strip()
            if spec.startswith("=="):
                return ("exact", spec[2:])
            if re.fullmatch(r"\d+\.\d+\.\d+(-[0-9A-Za-z.]+)?", spec):
                return ("range", "^" + spec)  # bare version = implicit caret under Poetry
            return ("range", spec)
    return None


def find_pin_cargo(content, pkg):
    namere = re.escape(pkg)
    m = re.search(rf'^\s*{namere}\s*=\s*\{{[^}}]*version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if not m:
        m = re.search(rf'^\s*{namere}\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if not m:
        return None
    spec = m.group(1).strip()
    if spec.startswith("="):
        return ("exact", spec[1:])
    if re.fullmatch(r"\d+\.\d+\.\d+(-[0-9A-Za-z.]+)?", spec):
        return ("range", spec)  # bare = implicit caret, not exact
    return ("range", spec)


def parse_pom_properties(content):
    """A POM's own top-level <properties> values - mirrors pkg/maven/pom.go's
    parsePOMProperties (no parent-POM or built-in property resolution)."""
    props = {}
    m = re.search(r"<properties>(.*?)</properties>", content, re.DOTALL)
    if not m:
        return props
    for entry in re.finditer(r"<([\w.-]+)>\s*([^<]*?)\s*</\1>", m.group(1)):
        props[entry.group(1)] = entry.group(2).strip()
    return props


def maven_pinned_version(requirement, props):
    """Resolve a Maven <version> against a POM's own <properties>, mirroring
    pkg/maven/pom.go's mavenPinnedVersion. Returns the resolved exact version,
    or None for a genuine range (bracket syntax) or unresolvable property."""
    requirement = requirement.strip()
    if not requirement:
        return None
    if requirement.startswith("${") and requirement.endswith("}") and requirement.count("${") == 1:
        resolved = props.get(requirement[2:-1])
        if not resolved or "${" in resolved:
            return None
        requirement = resolved
    elif "${" in requirement:
        return None
    if requirement.startswith("[") or requirement.startswith("("):
        return None
    return requirement


def find_pin_maven(content, pkg):
    group, artifact = pkg.split(":", 1)
    props = parse_pom_properties(content)
    for block in re.finditer(r"<dependency>(.*?)</dependency>", content, re.DOTALL):
        b = block.group(1)
        g = re.search(r"<groupId>\s*([^<]+?)\s*</groupId>", b)
        a = re.search(r"<artifactId>\s*([^<]+?)\s*</artifactId>", b)
        v = re.search(r"<version>\s*([^<]+?)\s*</version>", b)
        if g and a and g.group(1) == group and a.group(1) == artifact:
            if not v:
                return None
            raw = v.group(1).strip()
            resolved = maven_pinned_version(raw, props)
            return ("exact", resolved) if resolved is not None else ("range", raw)
    return None


def find_parent_maven(content):
    """A POM's own <parent> declaration - a dependency with no direct
    <version> (e.g. spring-boot-starter-*) is often actually pinned via its
    parent's dependencyManagement instead."""
    m = re.search(r"<parent>(.*?)</parent>", content, re.DOTALL)
    if not m:
        return None
    b = m.group(1)
    g = re.search(r"<groupId>\s*([^<]+?)\s*</groupId>", b)
    a = re.search(r"<artifactId>\s*([^<]+?)\s*</artifactId>", b)
    v = re.search(r"<version>\s*([^<]+?)\s*</version>", b)
    if not (g and a and v):
        return None
    raw = v.group(1).strip()
    parent_pkg = f"{g.group(1)}:{a.group(1)}"
    resolved = maven_pinned_version(raw, parse_pom_properties(content))
    return (parent_pkg, "exact", resolved) if resolved is not None else (parent_pkg, "range", raw)


def find_pin_go(content, pkg):
    for line in content.splitlines():
        line = re.sub(r"^require\s+", "", line.strip())
        m = re.match(rf"^{re.escape(pkg)}\s+(\S+)", line)
        if m:
            return ("exact", m.group(1))  # go.mod requires are always exact pins
    return None


def find_pin_ghactions(content, pkg):
    m = re.search(rf"uses:\s*{re.escape(pkg)}@(\S+)", content)
    if not m:
        return None
    ref = m.group(1).split("#")[0].strip()
    # A full commit SHA is yul's own preferred pin form for Actions (see
    # main.go's Suggested field / pkg/githubactions/sha.go) - it's just as
    # comparable as a version tag (yul_scan_outdated resolves it back to a
    # release under the hood), not an unpinned branch reference.
    if re.match(r"^v?\d", ref) or re.fullmatch(r"[0-9a-f]{40}", ref):
        return ("exact", ref)
    return ("range", ref)  # branch name: not comparable


PIN_FINDERS = {
    ("pypi", "requirements.txt"): find_pin_pypi_requirements,
    ("pypi", "pyproject.toml"): find_pin_pypi_pyproject,
    ("npm", "package.json"): find_pin_npm,
    ("cargo", "Cargo.toml"): find_pin_cargo,
    ("maven", "pom.xml"): find_pin_maven,
    ("go", "go.mod"): find_pin_go,
}


def find_pin(eco, manifest_filename, content, pkg):
    if eco == "githubactions":
        return find_pin_ghactions(content, pkg)
    finder = PIN_FINDERS.get((eco, manifest_filename))
    return finder(content, pkg) if finder else None


def short_pkg_name(pkg):
    """Last path/coordinate segment of a target package id, e.g.
    "junit:junit" -> "junit", "github.com/stretchr/objx" -> "objx" - used to
    hunt for it elsewhere in a manifest when the exact match fails, as a
    signal of a package swap (e.g. junit:junit -> org.junit.jupiter:junit-jupiter)."""
    return pkg.rsplit("/", 1)[-1].rsplit(":", 1)[-1]


def find_short_mentions(content, short_name):
    return [l.strip() for l in content.splitlines() if short_name.lower() in l.lower()]


# ---------------------------------------------------------------------------
# yul scan wrapper: is a given package flagged outdated in a rep dir's final
# manifest state?
# ---------------------------------------------------------------------------

_scan_cache = {}


def yul_scan_outdated(yul_bin, rep_dir):
    rep_dir = str(rep_dir)
    if rep_dir in _scan_cache:
        return _scan_cache[rep_dir]
    findings = {}
    try:
        # throwaway XDG_CACHE_HOME: yul's on-disk scan cache dedupes findings
        # it already "notified" for a given absolute path, which would
        # otherwise suppress repeat scans of these rep dirs across runs.
        with tempfile.TemporaryDirectory() as cache_home:
            out = subprocess.run(
                [yul_bin, "scan", "--project-dir", rep_dir],
                capture_output=True, text=True, timeout=30,
                env={"HOME": str(Path.home()), "XDG_CACHE_HOME": cache_home},
            )
        if out.stdout.strip():
            payload = json.loads(out.stdout)
            ctx = payload.get("hookSpecificOutput", {}).get("additionalContext", "")
            for line in ctx.splitlines():
                m = re.match(r"\s*(?:\S+:\s*)?(\S+)\s+\S+\s*->\s*(\S+)(?:\s*#.*)?\s*$", line)
                if m:
                    findings[m.group(1)] = m.group(2)
    except Exception:
        pass
    _scan_cache[rep_dir] = findings
    return findings


# ---------------------------------------------------------------------------
# Transcript: did yul's hook block+correct this package, and did a
# registry/package-manager lookup happen (curl/wget against a registry, or
# npm install / pip install / go get / cargo add / etc)?
# ---------------------------------------------------------------------------

REGISTRY_HOST_RE = re.compile(
    r"(pypi\.org|registry\.npmjs\.org|npmjs\.com|crates\.io|repo1\.maven\.org|"
    r"search\.maven\.org|proxy\.golang\.org|api\.github\.com/repos)"
)
PKG_MANAGER_CMD_RE = re.compile(
    r"\b(npm\s+(install|add|i\b)|pip\s+install|pip3\s+install|go\s+get|"
    r"cargo\s+add|mvn\s+(versions:|dependency:)|poetry\s+add|uv\s+add)"
)
CURL_WGET_RE = re.compile(r"\b(curl|wget)\b")


def analyze_transcript(path, pkg):
    mitigated_pkg, used_tool = False, False
    if not path.exists():
        return mitigated_pkg, used_tool
    with open(path) as f:
        for line in f:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            if obj.get("type") == "assistant":
                for c in obj["message"].get("content", []):
                    if c.get("type") != "tool_use" or c.get("name") != "Bash":
                        continue
                    cmd = c.get("input", {}).get("command", "")
                    if (CURL_WGET_RE.search(cmd) and REGISTRY_HOST_RE.search(cmd)) or PKG_MANAGER_CMD_RE.search(cmd):
                        used_tool = True

            if obj.get("type") == "user":
                for c in obj["message"].get("content", []):
                    if c.get("type") != "tool_result" or not c.get("is_error"):
                        continue
                    content = c.get("content", "")
                    if isinstance(content, list):
                        content = json.dumps(content)
                    if not isinstance(content, str):
                        continue
                    if re.search(r"PreToolUse:(Write|Edit) hook error", content) and "outdated dependencies" in content:
                        if pkg and re.search(rf"\b{re.escape(pkg.split(':')[-1])}\b", content):
                            mitigated_pkg = True
    return mitigated_pkg, used_tool


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir", nargs="?", default=str(HERE / "top-final"))
    ap.add_argument("--cases", default=str(HERE / "cases_top.json"))
    ap.add_argument("--top-packages", default=str(HERE / "top-packages.json"))
    ap.add_argument("--yul", default=str(REPO_ROOT / "yul"))
    ap.add_argument("--json-out", default=None)
    args = ap.parse_args()

    run_dir = Path(args.run_dir)
    meta = load_cases(args.cases, args.top_packages)
    rows = []

    for case_dir in sorted(p for p in run_dir.iterdir() if p.is_dir()):
        cid = case_dir.name
        if cid not in meta:
            continue
        info = meta[cid]
        eco, pkg = info["ecosystem"], info["package"]

        for condition in ("nohook", "hook"):
            cond_dir = case_dir / condition
            if not cond_dir.exists():
                continue
            for rep_dir in sorted(cond_dir.iterdir()):
                if not rep_dir.is_dir():
                    continue
                fm = rep_dir / "final_manifest"
                if not fm.exists():
                    continue
                content = fm.read_text()
                fmp = rep_dir / "final_manifest_path"
                manifest_name = fmp.read_text().strip() if fmp.exists() else (info["manifests"][0] if info["manifests"] else None)
                manifest_basename = Path(manifest_name).name if manifest_name else None

                pin = find_pin(eco, manifest_basename, content, pkg)
                is_exact = pin is not None and pin[0] == "exact"
                pin_kind = pin[0] if pin else "none"
                version = pin[1] if pin else None

                # maven: no direct <version> may still be pinned via <parent>'s
                # dependencyManagement (e.g. spring-boot-starter-*)
                if eco == "maven" and pin is None:
                    parent = find_parent_maven(content)
                    if parent and parent[1] == "exact" and parent[0].split(":", 1)[0] == pkg.split(":", 1)[0]:
                        is_exact, pin_kind, version = True, "via-parent", parent[2]

                # is_latest covers exact AND range pins: yul's own pins.Diff
                # flags a range that excludes latest too (recommending a
                # widened range), so a bare/caret/tilde spec that already
                # covers latest is just as "satisfied" as an exact pin at
                # latest - it's not a hook miss, there was simply nothing to
                # correct. Only pin_kind=="none" (package absent) is left
                # unresolved below.
                is_latest = None
                if pin_kind != "none":
                    outdated = yul_scan_outdated(args.yul, rep_dir)
                    short = short_pkg_name(pkg)
                    is_latest = not any(k == pkg or k == short or k.endswith("/" + short) for k in outdated)

                mitigated_pkg, used_tool = analyze_transcript(rep_dir / "transcript.jsonl", pkg)

                how = None
                if is_latest:
                    how = "hook" if (condition == "hook" and mitigated_pkg) else ("tool" if used_tool else "native")

                not_found_mentions = find_short_mentions(content, short_pkg_name(pkg)) if pin_kind == "none" else []

                rows.append({
                    "case": cid, "ecosystem": eco, "package": pkg, "condition": condition, "rep": rep_dir.name,
                    "pin_kind": pin_kind, "version": version, "is_exact": is_exact,
                    "is_latest": is_latest, "how": how, "not_found_mentions": not_found_mentions,
                })

    # ---------------- summary ----------------
    # "satisfied" = ended on an exact pin at latest, or a range that already
    # covered latest (yul's own pins.Diff checks both). native/tool/hook
    # classify *how* those satisfied reps got there and sum to "satisfied";
    # "via range" is the subset of "satisfied" reached through a range pin
    # rather than an exact one.
    def summarize(sub):
        latest = [r for r in sub if r["is_latest"]]
        how_counts = Counter(r["how"] for r in latest)
        via_range = sum(1 for r in latest if r["pin_kind"] == "range")
        return {
            "satisfied": f"{len(latest)}/{len(sub)}",
            "native": how_counts["native"], "tool": how_counts["tool"], "hook": how_counts["hook"],
            "via_range": via_range,
        }

    ecosystems = sorted({r["ecosystem"] for r in rows})
    cols = [("Condition", 10), ("Ecosystem", 14), ("Satisfied", 10), ("Native", 7), ("Tool", 6), ("Hook", 6), ("via range", 9)]

    def print_row(*vals):
        print(" | ".join(f"{v:<{w}}" if isinstance(v, str) else f"{v:<{w}}" for v, (_, w) in zip(vals, cols)))

    print("=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print_row(*[h for h, _ in cols])
    print_row(*["-" * w for _, w in cols])
    for condition in ("nohook", "hook"):
        sub = [r for r in rows if r["condition"] == condition]
        s = summarize(sub)
        print_row(condition, "all", s["satisfied"], s["native"], s["tool"], s["hook"], s["via_range"])
        for eco in ecosystems:
            s = summarize([r for r in sub if r["ecosystem"] == eco])
            print_row(condition, eco, s["satisfied"], s["native"], s["tool"], s["hook"], s["via_range"])

    # ---------------- hook condition: why a rep did NOT end up latest ----------------
    # nohook not being latest is expected (no memory of the latest release,
    # not investigated). hook is supposed to force every exact pin to latest,
    # so anything else here is worth a manual look.
    print()
    print("=" * 100)
    print("HOOK CONDITION: reps that did NOT end up satisfied")
    print("=" * 100)
    hook_rows = [r for r in rows if r["condition"] == "hook"]
    hook_outdated = [r for r in hook_rows if r["pin_kind"] != "none" and not r["is_latest"]]
    hook_not_found = [r for r in hook_rows if r["pin_kind"] == "none"]

    print(f"\nPin present but still outdated / range excludes latest (yul should have blocked this): {len(hook_outdated)} reps")
    for r in hook_outdated:
        print(f"  - {r['case']}/{r['rep']}: {r['package']} ({r['pin_kind']}) = {r['version']}")

    print(f"\nTarget package not found at all in the final manifest: {len(hook_not_found)} reps")
    for r in hook_not_found:
        if r["not_found_mentions"]:
            print(f"  - {r['case']}/{r['rep']}: {r['package']} absent, but its short name turns up elsewhere (possible package swap):")
            for m in r["not_found_mentions"][:3]:
                print(f"        {m}")
        else:
            print(f"  - {r['case']}/{r['rep']}: {r['package']} absent, no trace of it anywhere (likely never added)")

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(rows, indent=2))
        print(f"\nWrote raw per-rep rows to {args.json_out}")


if __name__ == "__main__":
    main()
