#!/usr/bin/env python3
"""Classify every benchmark rep of the 60 top-package cases, across all six
ecosystems, the way the paper's RQ1/RQ2 table does, and explain each rep that
does not end on the latest release.

Per rep, the target is the package the case is built around (case N in
cases_top.json maps to the Nth entry of its ecosystem in the snapshot). When
the target is absent but a known substitute is declared instead (SUBSTITUTES,
e.g. httpx for requests, mysql-connector-j for mysql-connector-java), the
substitute is judged against its own latest release. A rep is:

  absent          neither the target nor a substitute is declared (excluded,
                  as in the paper; annotations say why, e.g. stdlib only)
  already_latest  nohook: the final pin is latest.
                  hook: the final pin is latest and the hook never rejected a
                  stale pin of it (a rejected pin that was already latest, i.e.
                  a false positive, does not count as a rejection)
  mitigated       hook only: the hook rejected a stale pin and the final pin is
                  latest
  stale           the final pin is not latest; in the hook condition this is a
                  stale candidate the hook did not mitigate. A hook rep whose
                  pin was rejected but never rewritten (the agent gave up) also
                  ends here rather than being excluded.

A pin "is latest" if it is an exact pin of the latest release or, by default,
a range that admits it (`>=2.2,<3`, `^5.0.1`, Cargo's bare `0.62`, a floating
Actions tag like `v7`). With --strict-ranges a range only counts if its lower
bound is the latest release, and floating tags never count.

Route says where the final version came from: "tool" if a registry lookup or
a version-resolving package-manager command (`npm install pkg`, `uv add pkg`,
`cargo add pkg`, `go get pkg@latest`, `go mod tidy`) for the package happened
before the write that produced the final pin, else "memory".

<run_dir>/annotations.json, if present, holds the manual review of that run
set: a reason code and note per rep (see REASONS), plus per-case notes.

Usage:
    python3 benchmark/analyze_runs.py [RUN_DIR] [--strict-ranges] [--no-substitutes]
        [--latex] [--runs] [--json-out PATH]

No network access needed: latest versions come from the snapshot and
SUBSTITUTES.
"""
import argparse
import json
import re
import tomllib
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

from packaging.requirements import InvalidRequirement, Requirement
from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import InvalidVersion, Version

HERE = Path(__file__).resolve().parent

ECOSYSTEMS = {  # case id prefix -> (snapshot key, display name)
    "maven": ("maven", "Maven"),
    "ghactions": ("githubactions", "GitHub Actions"),
    "pypi": ("pypi", "PyPI"),
    "npm": ("npm", "npm"),
    "go": ("go", "Go"),
    "cargo": ("cargo", "Cargo"),
}

# Packages the agents declare instead of the snapshot target, judged against
# their own latest release (stable releases as of 2026-10-03, when the
# claude-code-opus runs were made). A substitute that is itself a snapshot
# target (e.g. actions/setup-node) takes its latest from the snapshot instead.
# The first one present in the final manifest is used.
SUBSTITUTES = {
    "requests": [("httpx", "0.28.1")],
    "urllib3": [("httpx", "0.28.1")],  # transport-level pooling and retries
    "pytz": [("tzdata", "2026.4")],  # stdlib zoneinfo plus the IANA database
    "fsevents": [("@parcel/watcher", "2.6.0")],  # maintained native FSEvents binding
    "resolve": [("enhanced-resolve", "5.26.0")],  # webpack's resolver
    "junit:junit": [  # JUnit 4 -> Jupiter
        ("org.junit.jupiter:junit-jupiter", "6.1.3"),
        ("org.junit:junit-bom", "6.1.3"),
    ],
    "mysql:mysql-connector-java": [("com.mysql:mysql-connector-j", "26.7.0")],  # relocated
    "org.springframework.boot:spring-boot-starter-web": [  # Boot 4 rename
        ("org.springframework.boot:spring-boot-starter-webmvc", "4.1.1"),
    ],
    "org.springframework.boot:spring-boot-starter-test": [  # Boot 4 per-technology test starters
        ("org.springframework.boot:spring-boot-starter-webmvc-test", "4.1.1"),
    ],
    "com.google.code.gson:gson": [  # the prompt only asks for JSON, never names gson
        ("tools.jackson.core:jackson-databind", "3.2.3"),
        ("tools.jackson:jackson-bom", "3.2.3"),
        ("com.fasterxml.jackson.core:jackson-databind", "2.22.3"),
        ("com.fasterxml.jackson:jackson-bom", "2.22.3"),
    ],
    "github.com/pmezard/go-difflib": [("github.com/aymanbagabas/go-udiff", "v0.4.1")],
    "gopkg.in/check.v1": [("github.com/stretchr/testify", None)],  # the prompt asks for gocheck-style suites; testify/suite has them
    "winapi": [("windows-sys", "0.61.2"), ("windows", "0.62.2")],  # Microsoft's successors
    "winapi-x86_64-pc-windows-gnu": [
        ("windows-sys", "0.61.2"),
        ("windows-targets", "0.53.5"),
        ("windows_x86_64_gnu", "0.53.1"),
    ],
    "winapi-i686-pc-windows-gnu": [
        ("windows-sys", "0.61.2"),
        ("windows-targets", "0.53.5"),
        ("windows_i686_gnu", "0.53.1"),
    ],
    "actions/cache": [("actions/setup-node", None)],  # setup-node's built-in `cache:` input
}

# Reason codes used in annotations.json and derived automatically below.
REASONS = {
    "no-dependency": "implemented with the standard library or its own code, declared nothing (excluded)",
    "memory-stale": "typed a version from memory, with no lookup, that is older than latest",
    "deliberate-compat": "knew or looked up latest but pinned an older release for task/environment compatibility",
    "blocked-agent-declined": "the hook rejected the stale pin and the agent never rewrote the dependency",
    "hook-blind-spot": "stale pin written somewhere the hook does not inspect",
    "stale-after-lookup": "looked the package up but still pinned an older release (needs manual review)",
    "admits-latest-only": "the range or floating tag admits latest but starts below it (stale only under --strict-ranges; "
                          "yul accepts such ranges by design)",
    "hook-miss": "hook rep ended stale for an unknown reason (needs manual review)",
    "not-declared": "target and substitutes absent (needs manual review)",
}

MANIFEST_NAMES = (r"(?:pom\.xml|requirements[\w.-]*\.txt|pyproject\.toml|package\.json|go\.mod|Cargo\.toml"
                  r"|\.github/workflows/[^\s'\"]+\.ya?ml)")
MANIFEST_RE = re.compile(MANIFEST_NAMES)
# shell constructs that rewrite a manifest: the ones yul's own bash check
# looks for (redirect, tee, sed -i, ... aimed at the manifest), plus scripts
SHELL_WRITE_RE = re.compile(
    r">>?\s*['\"]?(?:[^\s'\"]*/)?" + MANIFEST_NAMES + r"['\"]?(\s|;|&|\||$)"
    r"|\b(?:tee|sed\s+-i|perl\s+-i|cp|mv)\b[^;&|\n]*" + MANIFEST_NAMES +
    r"|open\([^)]*['\"]w['\"]|writeFileSync|\bnpm\s+pkg\s+set\b|\bgo\s+mod\s+edit\b")
LOOKUP_CMD_RE = re.compile(
    r"\bnpm\s+(view|info|show|v)\b|\bpip3?\s+(index\s+versions|download)\b|\bcargo\s+(search|info)\b"
    r"|\bgo\s+list\s+-m\b|\bgo\s+mod\s+download\b|\bgit\s+ls-remote\b|\bgh\s+(api|release)\b"
    r"|\bmvn\s+\S*(versions:|dependency:)")
REGISTRY_HOST_RE = re.compile(
    r"pypi\.org|registry\.npmjs\.org|npmjs\.com|crates\.io|proxy\.golang\.org|pkg\.go\.dev"
    r"|repo1?\.maven(\.apache)?\.org|search\.maven\.org|central\.sonatype|api\.github\.com|github\.com/")
PKG_MANAGER_RE = re.compile(
    r"\b(npm|pnpm|yarn)\s+(install|i|add)\b|\buv\s+add\b|\bpoetry\s+add\b|\bpip3?\s+install\b"
    r"|\bcargo\s+add\b|\bgo\s+get\b")
GO_IMPLICIT_RE = re.compile(r"\bgo\s+(mod\s+tidy|build|run|test|vet)\b")

PIN_LINE_RE = re.compile(r"^\s+(\S+)\s+(\S+)\s+->\s+(\S+)", re.MULTILINE)
RANGE_LINE_RE = re.compile(r"^\s+(\S+)\s+(.+?) does not allow latest (\S+) -> update range to (\S+)", re.MULTILINE)


# ---------------------------------------------------------------------------
# Version ranges: does a declared spec admit the latest release, and is its
# lower bound the latest release?
# ---------------------------------------------------------------------------

def _semver(text):
    """'1.2' -> ((1, 2, 0), 2): numeric parts padded to three, plus how many
    were given. None for anything that isn't a plain dotted version."""
    m = re.fullmatch(r"v?(\d+)(?:\.(\d+|[xX*]))?(?:\.(\d+|[xX*]))?(?:[-+].*)?", text.strip())
    if not m:
        return None
    parts = [p for p in m.groups() if p is not None and p not in ("x", "X", "*")]
    nums = tuple(int(p) for p in parts) + (0,) * (3 - len(parts))
    return nums, len(parts)


def _caret(nums, given):
    major, minor, patch = nums
    if given == 1 or major > 0:
        upper = (major + 1, 0, 0)
    elif given == 2 or minor > 0:
        upper = (0, minor + 1, 0)
    else:
        upper = (0, 0, patch + 1)
    return nums, upper


def _tilde(nums, given):
    major, minor, _ = nums
    return nums, ((major + 1, 0, 0) if given == 1 else (major, minor + 1, 0))


def _comparator(op, text, bare):
    """[lower, upper) bounds (None = open) for one npm/Cargo comparator. bare
    is how a version with no operator reads: "exact" (npm) or "caret" (Cargo)."""
    if text in ("", "*", "x", "X", "latest"):
        return None, None
    parsed = _semver(text)
    if parsed is None:
        raise ValueError(text)
    nums, given = parsed
    if op == "" and given < 3:
        op = "^" if bare == "caret" else "~"  # npm reads "1.2" as 1.2.x
    if op == "^" or (op == "" and bare == "caret"):
        return _caret(nums, given)
    if op == "~":
        return _tilde(nums, given)
    if op in ("", "="):
        return nums, nums[:2] + (nums[2] + 1,)
    if op == ">=":
        return nums, None
    if op == ">":
        return nums[:2] + (nums[2] + 1,), None
    if op == "<":
        return None, nums
    if op == "<=":
        return None, nums[:2] + (nums[2] + 1,)
    raise ValueError(op)


def semver_range(spec, bare):
    """Parses an npm/Cargo requirement into alternatives of [lower, upper)
    bounds. Returns None if it can't."""
    alternatives = []
    for alt in spec.split("||"):
        lower, upper = None, None
        tokens = re.findall(r"(\^|~|>=|<=|>|<|=)?\s*([^\s,^~<>=]+)", alt)
        if not tokens:
            tokens = [("", "")]
        try:
            for op, text in tokens:
                lo, up = _comparator(op or "", text, bare)
                if lo is not None and (lower is None or lo > lower):
                    lower = lo
                if up is not None and (upper is None or up < upper):
                    upper = up
        except ValueError:
            return None
        alternatives.append((lower, upper))
    return alternatives


def judge_semver(spec, latest, bare):
    """(kind, admits_latest, floor_is_latest) for an npm/Cargo spec."""
    spec = spec.strip()
    exact = re.fullmatch(r"=?\s*v?(\d+\.\d+\.\d+(?:-[\w.]+)?)", spec) if bare == "exact" else \
        re.fullmatch(r"=\s*(\d+\.\d+\.\d+(?:-[\w.]+)?)", spec)
    target = _semver(latest)[0]
    if exact:
        same = _semver(exact.group(1))[0] == target
        return "exact", same, same
    ranges = semver_range(spec, bare)
    if ranges is None:
        return "unparsed", False, False
    admits = any((lo is None or lo <= target) and (up is None or target < up) for lo, up in ranges)
    floor = any(lo == target for lo, _ in ranges)
    return ("unpinned" if all(lo is None for lo, _ in ranges) else "range"), admits, floor


def _strip_post(text):
    # a post-release (2.9.0.post0) is the same release as far as "latest" goes
    return re.sub(r"\.?post\d*", "", text)


def judge_pypi(spec, latest):
    latest = Version(_strip_post(latest))
    spec = _strip_post(spec)
    if not spec:
        return "unpinned", True, False
    try:
        specifiers = SpecifierSet(spec)
    except InvalidSpecifier:
        return "unparsed", False, False
    ops = [(s.operator, s.version) for s in specifiers]
    floors = [Version(v) for op, v in ops if op in ("==", "===", ">=", "~=", ">") and "*" not in v]
    admits = specifiers.contains(latest, prereleases=True)
    floor = bool(floors) and max(floors) == latest
    if len(ops) == 1 and ops[0][0] in ("==", "===") and "*" not in ops[0][1]:
        return "exact", admits, admits
    return "range", admits, floor


def judge_ghactions(ref, latest):
    sha, _, tag = latest.partition("#")
    sha, tag = sha.strip(), tag.strip()
    if ref == sha:
        return "sha", True, True
    if ref == tag:
        return "tag", True, True
    if re.fullmatch(r"[0-9a-f]{40}", ref):
        return "other-sha", False, False
    if re.fullmatch(r"v?\d+(\.\d+)?", ref):
        return "floating", tag.lstrip("v").startswith(ref.lstrip("v") + "."), False
    return "tag", False, False


def judge(eco, spec, latest):
    """(kind, admits_latest, floor_is_latest)."""
    if spec is None:
        return "unresolved", False, False
    if eco == "pypi":
        return judge_pypi(spec, latest)
    if eco == "npm":
        return judge_semver(spec, latest, "exact")
    if eco == "cargo":
        return judge_semver(spec, latest, "caret")
    if eco == "githubactions":
        return judge_ghactions(spec, latest)
    same = spec.strip() == latest.strip()  # Maven and Go only pin exact versions
    return "exact", same, same


# ---------------------------------------------------------------------------
# Final manifests: {package: spec} per ecosystem. Cargo and Go also record
# where the entry lives (target-specific table, `// indirect`).
# ---------------------------------------------------------------------------

def canon_pypi(name):
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_pypi(content, filename):
    deps = {}

    def add(line):
        try:
            req = Requirement(line)
        except InvalidRequirement:
            return
        deps.setdefault(canon_pypi(req.name), str(req.specifier))

    if filename.endswith(".txt"):
        for line in content.splitlines():
            line = line.split("#", 1)[0].strip()
            if line and not line.startswith("-"):
                add(line)
        return deps
    data = tomllib.loads(content)
    project = data.get("project", {})
    lines = list(project.get("dependencies", []))
    for group in project.get("optional-dependencies", {}).values():
        lines += group
    for group in data.get("dependency-groups", {}).values():
        lines += [r for r in group if isinstance(r, str)]
    for line in lines:
        add(line)
    poetry = data.get("tool", {}).get("poetry", {})
    tables = [poetry.get("dependencies", {})] + [g.get("dependencies", {}) for g in poetry.get("group", {}).values()]
    for table in tables:
        for name, spec in table.items():
            if name != "python":
                spec = spec.get("version", "") if isinstance(spec, dict) else spec
                deps.setdefault(canon_pypi(name), spec.replace("^", "~=") if spec.startswith("^") else spec)
    return deps


def parse_npm(content, _):
    data = json.loads(content)
    deps = {}
    for field in ("dependencies", "devDependencies", "optionalDependencies", "peerDependencies"):
        for name, spec in data.get(field, {}).items():
            deps.setdefault(name, spec)
    return deps


def parse_cargo(content, _):
    data = tomllib.loads(content)
    deps, where = {}, {}
    tables = [("", data)] + [(f"target.{cfg}.", t) for cfg, t in data.get("target", {}).items()]
    for prefix, table in tables:
        for kind in ("dependencies", "dev-dependencies", "build-dependencies"):
            for key, value in table.get(kind, {}).items():
                if isinstance(value, dict):
                    name, spec = value.get("package", key), value.get("version")
                else:
                    name, spec = key, value
                if spec is not None and name not in deps:
                    deps[name] = spec
                    where[name] = prefix + kind
    return deps, where


def parse_go(content, _):
    deps, indirect = {}, set()
    in_block = False
    for raw in content.splitlines():
        line = raw.strip()
        if line.startswith("require ("):
            in_block = True
            continue
        if in_block and line == ")":
            in_block = False
            continue
        m = re.match(r"^(?:require\s+)?(\S+)\s+(v\S+)(\s*//\s*indirect)?", line) if (in_block or line.startswith("require ")) else None
        if m:
            deps.setdefault(m.group(1), m.group(2))
            if m.group(3):
                indirect.add(m.group(1))
    return deps, indirect


PROPERTY_RE = re.compile(r"\$\{([^}]+)\}")


def parse_maven(content, _):
    """{group:artifact: version} for every dependency and plugin, with
    properties resolved. A version-less dependency inherits from the
    spring-boot-starter-parent or from an imported BOM of the same group
    family (slf4j-bom -> slf4j-api, junit-bom -> junit-jupiter); the second
    dict maps such a dependency to the parent or BOM it inherits from."""
    root = ET.fromstring(content)
    for el in root.iter():
        el.tag = el.tag.rpartition("}")[2]

    def text(el, tag):
        child = el.find(tag) if el is not None else None
        return child.text.strip() if child is not None and child.text else None

    properties = root.find("properties")
    props = {p.tag: (p.text or "").strip() for p in properties} if properties is not None else {}
    parent = root.find("parent")
    parent_group, parent_version = text(parent, "groupId"), text(parent, "version")
    parent_ga = f"{parent_group}:{text(parent, 'artifactId')}"
    props["project.version"] = text(root, "version") or parent_version or ""
    props["project.parent.version"] = parent_version or ""

    def resolve(version):
        for _ in range(5):
            expanded = PROPERTY_RE.sub(lambda m: props.get(m.group(1), m.group(0)), version)
            if expanded == version:
                break
            version = expanded
        return None if PROPERTY_RE.search(version) else version

    boms = []
    managed = root.find("dependencyManagement")
    for dep in (managed.iter("dependency") if managed is not None else []):
        if text(dep, "scope") == "import" and text(dep, "version"):
            boms.append((text(dep, "groupId"), text(dep, "artifactId"), resolve(text(dep, "version"))))

    pins, sources = {}, {}
    for el in root.iter():
        if el.tag not in ("dependency", "plugin"):
            continue
        group = text(el, "groupId") or ("org.apache.maven.plugins" if el.tag == "plugin" else None)
        artifact = text(el, "artifactId")
        if not group or not artifact:
            continue
        ga, version, source = f"{group}:{artifact}", text(el, "version"), None
        if version is not None:
            version = resolve(version)
        elif group == "org.springframework.boot" and parent_group == "org.springframework.boot":
            version, source = parent_version, parent_ga
        else:
            bom = next((b for b in boms if b[0] and (group == b[0] or group.startswith(b[0] + "."))), None)
            if bom:
                version, source = bom[2], f"{bom[0]}:{bom[1]}"
        if pins.get(ga) is None:
            pins[ga] = version
            if source:
                sources[ga] = source
    return pins, sources


USES_RE = re.compile(r"^\s*-?\s*uses:\s*['\"]?([^\s@'\"#]+)@([^\s'\"#]+)", re.MULTILINE)


def parse_ghactions(content, _):
    deps = {}
    for m in USES_RE.finditer(content):
        deps.setdefault(m.group(1), m.group(2))
    return deps


def parse_manifest(eco, content, filename):
    """Returns (deps, extra): extra is Cargo's table per crate, Go's set of
    indirect requires, or the parent/BOM each Maven artifact inherits from."""
    if eco == "cargo":
        return parse_cargo(content, filename)
    if eco == "go":
        return parse_go(content, filename)
    if eco == "maven":
        return parse_maven(content, filename)
    parser = {"pypi": parse_pypi, "npm": parse_npm, "githubactions": parse_ghactions}[eco]
    return parser(content, filename), None


# ---------------------------------------------------------------------------
# Transcript: when was each package looked up, declared (typed or resolved by
# a package manager), and rejected by the hook?
# ---------------------------------------------------------------------------

def mention_re(eco, name):
    """Regex for a package's appearance in a command or file: its name, or the
    path form registries use (org/slf4j/slf4j-api, actions/$repo)."""
    if eco == "maven":
        group, _, artifact = name.partition(":")
        forms = [re.escape(artifact) + r"(?![\w.-])"]
    elif eco == "githubactions":
        forms = [re.escape(name), r"(?<![\w-])" + re.escape(name.split("/")[1]) + r"(?![\w-])"]
    elif eco == "go":
        forms = [re.escape(name), re.escape("/".join(name.split("/")[-2:]))]
    elif eco == "pypi":
        forms = [r"(?<![\w-])" + name.replace("-", "[-_.]") + r"(?![\w-])"]
    else:
        forms = [r"(?<![\w-])" + re.escape(name) + r"(?![\w-])"]
    return re.compile("|".join(forms), re.IGNORECASE)


def explicit_version(cmd, name_re):
    """True if a package-manager command names the package with a version
    (`pkg@1.2`, `pkg==1.2`, `pkg>=1.2`), i.e. the agent typed the version."""
    for m in name_re.finditer(cmd):
        if re.match(r"@v?\d|@[\^~]|\s*(==|>=|~=|<=|>|<)", cmd[m.end():]):
            return True
    return False


def load_events(path):
    """Ordered tool calls with their results."""
    events, by_id = [], {}
    fallback = False
    for raw in path.read_text().splitlines():
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if obj.get("type") == "system" and obj.get("subtype") == "model_refusal_fallback":
            fallback = obj.get("fallback_model") or True
        content = obj.get("message", {}).get("content") if isinstance(obj.get("message"), dict) else None
        if not isinstance(content, list):
            continue
        for c in content:
            if obj.get("type") == "assistant" and c.get("type") == "tool_use":
                ev = {"tool": c["name"], "input": c.get("input", {}), "result": "", "error": False}
                by_id[c["id"]] = ev
                events.append(ev)
            elif obj.get("type") == "user" and c.get("type") == "tool_result" and c.get("tool_use_id") in by_id:
                body = c.get("content", "")
                if isinstance(body, list):
                    body = "\n".join(x.get("text", "") for x in body if isinstance(x, dict))
                ev = by_id[c["tool_use_id"]]
                ev["result"], ev["error"] = str(body), bool(c.get("is_error"))
    return events, fallback


def hook_rejections(ev):
    """{package: rejected spec} for a stale-pin rejection, None otherwise (a
    plain "use Write/Edit, not bash" rejection names no package)."""
    text = ev["result"]
    if not ev["error"] or "hook error" not in text:
        return None
    if "outdated dependenc" not in text and "pinned ranges need attention" not in text:
        return None
    found = {m.group(1): m.group(2) for m in RANGE_LINE_RE.finditer(text)}
    for m in PIN_LINE_RE.finditer(text):
        if "does not allow latest" not in m.group(0):
            found.setdefault(m.group(1), m.group(2))
    return found


def analyze_transcript(events, eco, names):
    """For a set of equivalent package names (target plus substitutes):
    lookups, declarations, and hook rejections, as event indexes."""
    res = [(n, mention_re(eco, n)) for n in names]
    lookups, decls, rejected = [], [], []

    def mentions(text):
        return any(r.search(text) for _, r in res)

    for i, ev in enumerate(events):
        tool, inp = ev["tool"], ev["input"]
        blocked = ev["error"] and "hook error" in ev["result"]
        rej = hook_rejections(ev)
        if rej:
            for name, old in rej.items():
                if any(name == n or name.lower() == n.lower() for n in names):
                    rejected.append((i, name, old))
        if tool == "Bash":
            cmd = inp.get("command", "")
            if mentions(cmd) and (LOOKUP_CMD_RE.search(cmd) or (re.search(r"\b(curl|wget)\b", cmd) and REGISTRY_HOST_RE.search(cmd))):
                lookups.append(i)
            if PKG_MANAGER_RE.search(cmd) and mentions(cmd):
                typed = any(explicit_version(cmd, r) for _, r in res)
                decls.append({"i": i, "how": "typed" if typed else "resolved", "blocked": blocked})
            elif eco == "go" and GO_IMPLICIT_RE.search(cmd) and any(
                    re.search(rf"go: (added|found) \S*{re.escape(n)}", ev["result"]) for n in names):
                decls.append({"i": i, "how": "resolved", "blocked": blocked})
            elif SHELL_WRITE_RE.search(cmd) and MANIFEST_RE.search(cmd) and mentions(cmd):
                decls.append({"i": i, "how": "typed", "blocked": blocked})
        elif tool in ("Write", "Edit"):
            body = inp.get("content") or inp.get("new_string") or ""
            if MANIFEST_RE.search(inp.get("file_path", "")) and mentions(body):
                decls.append({"i": i, "how": "typed", "blocked": blocked})
        elif tool in ("WebFetch", "WebSearch") and mentions(json.dumps(inp)):
            lookups.append(i)
    return lookups, decls, rejected


# ---------------------------------------------------------------------------
# Snapshot check: no rep may end up with a release newer than the recorded
# latest, or the snapshot (or SUBSTITUTES) was out of date when the runs were
# made.
# ---------------------------------------------------------------------------

LOCKFILES = ("Cargo.lock", "uv.lock", "poetry.lock", "package-lock.json", "go.sum")
SKIP_DIRS = {"target", "node_modules", ".venv", "venv", ".git", "__pycache__"}


def recorded_latest(case, name, snapshot):
    eco, target = case["eco"], case["target"]
    same = (lambda a, b: canon_pypi(a) == canon_pypi(b)) if eco == "pypi" else (lambda a, b: a == b)
    if same(name, target):
        return case["latest"]
    for sub, latest in SUBSTITUTES.get(target, []):
        if same(name, sub):
            return latest or snapshot[eco][sub]
    return None


def release_key(eco, text):
    """Orderable key for a stable release; None for pre-releases, SHAs and Go
    pseudo-versions, which are left out of the comparison."""
    text = text.split("#")[-1].strip().lstrip("v=")
    if eco == "pypi":
        try:
            version = Version(text)
        except InvalidVersion:
            return None
        return None if version.is_prerelease else version
    m = re.fullmatch(r"\d+(\.\d+)*", text)
    return tuple(int(n) for n in text.split(".")) if m else None


def spec_versions(eco, spec):
    """The exact version or lower bounds a declared spec names (upper bounds
    like <3 are not pins)."""
    if eco == "pypi":
        try:
            return [s.version for s in SpecifierSet(spec) if s.operator in ("==", "===", ">=", "~=", ">")]
        except InvalidSpecifier:
            return []
    if eco in ("npm", "cargo"):
        return [v for op, v in re.findall(r"(\^|~|>=|<=|>|<|=)?\s*v?(\d+(?:\.\d+)*)", spec) if op not in ("<", "<=")]
    return [spec]


def locked_versions(rep_dir, eco, names):
    """(lockfile, package, version) for the given packages in any lockfile the
    rep left behind, outside build and dependency directories."""
    wanted = {canon_pypi(n) if eco == "pypi" else n for n in names}
    found = []
    for path in sorted(rep_dir.rglob("*")):
        if path.name not in LOCKFILES or SKIP_DIRS & set(path.relative_to(rep_dir).parts[:-1]):
            continue
        text = path.read_text(errors="replace")
        if path.name == "package-lock.json":
            try:
                packages = json.loads(text).get("packages", {})
            except json.JSONDecodeError:
                continue
            entries = [(k.rpartition("node_modules/")[2], p.get("version", "")) for k, p in packages.items() if k]
        elif path.name == "go.sum":
            entries = [(line.split()[0], line.split()[1].removesuffix("/go.mod")) for line in text.splitlines() if line.strip()]
        else:
            entries = re.findall(r'^name = "([^"]+)"\nversion = "([^"]+)"', text, re.MULTILINE)
        for pkg, version in entries:
            if (canon_pypi(pkg) if eco == "pypi" else pkg) in wanted:
                found.append((path.name, pkg, version))
    return found


def hook_suggestions(events):
    """(package, version) for every version a hook rejection told the agent to use."""
    found = []
    for ev in events:
        if hook_rejections(ev) is None:
            continue
        text = ev["result"]
        for m in RANGE_LINE_RE.finditer(text):
            found.append((m.group(1), m.group(3)))
        for m in re.finditer(r"^\s+(\S+)\s+\S+\s+->\s+(\S+)(?:\s+#\s+(\S+))?$", text, re.MULTILINE):
            if "does not allow latest" not in m.group(0):
                found.append((m.group(1), m.group(3) or m.group(2)))
    return found


def newer_than_recorded(case, rep_dir, name, spec, names, events, snapshot):
    eco = case["eco"]
    sources = [("manifest", name, v) for v in (spec_versions(eco, spec) if name and spec else [])]
    sources += [(lock, pkg, v) for lock, pkg, v in locked_versions(rep_dir, eco, names)]
    sources += [("hook suggestion", pkg, v) for pkg, v in hook_suggestions(events)]
    newer = []
    for source, pkg, version in sources:
        latest = recorded_latest(case, pkg, snapshot)
        if latest is None:
            continue
        have, want = release_key(eco, version), release_key(eco, latest)
        if have is not None and want is not None and have > want:
            newer.append(f"{source}: {pkg} {version} > recorded {latest.split('#')[-1].strip()}")
    return sorted(set(newer))


def route_of(decl, lookups, decls):
    """tool if the declaration was resolved by a package manager, or a lookup
    or package-manager resolution of the package came before it."""
    if decl is None:
        return None
    if decl["how"] == "resolved":
        return "tool"
    earlier = any(i < decl["i"] for i in lookups) or any(d["how"] == "resolved" and d["i"] < decl["i"] for d in decls)
    return "tool" if earlier else "memory"


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def load_targets(cases_path, snapshot_path):
    snapshot = json.loads(Path(snapshot_path).read_text())["ecosystems"]
    cases = {}
    for c in json.loads(Path(cases_path).read_text()):
        m = re.match(r"^(pypi|maven|npm|go|cargo|ghactions)-top-(\d+)-", c["id"])
        if not m:
            continue
        eco = ECOSYSTEMS[m.group(1)][0]
        name = list(snapshot[eco])[int(m.group(2)) - 1]
        cases[c["id"]] = {"eco": eco, "target": name, "latest": snapshot[eco][name],
                          "seed": c.get("seed") or "", "prompt": c["prompt"]}
    return cases, snapshot


def declared(case, deps, snapshot, use_substitutes):
    """(name, latest, is_substitute) for the target, or the first substitute
    present, in the final manifest."""
    eco, target = case["eco"], case["target"]
    key = canon_pypi(target) if eco == "pypi" else target
    if key in deps:
        return key, case["latest"], False
    if use_substitutes:
        for name, latest in SUBSTITUTES.get(target, []):
            if name in deps:
                return name, latest or snapshot[eco][name], True
    return None, None, False


def classify(case, condition, rep_dir, snapshot, args, annotation, case_annotation):
    eco = case["eco"]
    content = (rep_dir / "final_manifest").read_text() if (rep_dir / "final_manifest").exists() else ""
    path_file = rep_dir / "final_manifest_path"
    filename = path_file.read_text().strip() if path_file.exists() else ""
    deps, extra = {}, None
    if content.strip() and content.strip() != "MANIFEST_NOT_WRITTEN":
        try:
            deps, extra = parse_manifest(eco, content, filename)
        except (ValueError, ET.ParseError, tomllib.TOMLDecodeError, json.JSONDecodeError):
            deps = {}
    name, latest, substitute = declared(case, deps, snapshot, not args.no_substitutes)

    names = [case["target"]]
    if not args.no_substitutes:
        names += [n for n, _ in SUBSTITUTES.get(case["target"], [])]
    if eco == "maven" and name in (extra or {}):
        names.append(extra[name])  # the version came from this parent or BOM
    events, fallback = load_events(rep_dir / "transcript.jsonl")
    lookups, decls, rejected = analyze_transcript(events, eco, names)
    final_decl = next((d for d in reversed(decls) if not d["blocked"]), None)
    first_decl = decls[0] if decls else None

    row = {
        "case": rep_dir.parent.parent.name, "ecosystem": eco, "condition": condition, "rep": rep_dir.name,
        "target": case["target"], "declared": name, "substitute": substitute, "spec": deps.get(name) if name else None,
        "latest": latest, "kind": None, "outcome": None, "route": None, "first_route": route_of(first_decl, lookups, decls),
        "rejected": [f"{n} {old}" for _, n, old in rejected], "fallback_model": fallback,
        "location": (extra or {}).get(name) if eco == "cargo" and name else None,
        "reason": None, "note": annotation.get("note", ""),
        "newer": newer_than_recorded(case, rep_dir, name, deps.get(name) if name else None, names, events, snapshot),
    }
    rejected_stale = [old for _, _, old in rejected if not is_latest(judge(eco, old, latest or case["latest"]), args)]

    if name is None:
        if condition == "hook" and rejected:
            row["outcome"], row["reason"] = "stale", "blocked-agent-declined"
        else:
            row["outcome"], row["reason"] = "absent", "not-declared"
    else:
        verdict = judge(eco, row["spec"], latest)
        row["kind"] = verdict[0]
        latest_ok = is_latest(verdict, args)
        row["route"] = route_of(final_decl, lookups, decls)
        if condition == "nohook" or not rejected_stale:
            row["outcome"] = "already_latest" if latest_ok else "stale"
        else:
            row["outcome"] = "mitigated" if latest_ok else "stale"
        if row["outcome"] == "stale":
            if verdict[1]:
                row["reason"] = "admits-latest-only"
            elif condition == "hook" and row["location"] and row["location"].startswith("target."):
                row["reason"] = "hook-blind-spot"
            elif condition == "hook":
                row["reason"] = "hook-miss"
            else:
                row["reason"] = "memory-stale" if row["route"] == "memory" else "stale-after-lookup"
    # manual review: a rep's own reason wins over the case's default for its outcome
    default = case_annotation.get(f"{row['outcome']}_reason")
    if row["outcome"] in ("absent", "stale") and (annotation.get("reason") or default):
        row["reason"] = annotation.get("reason") or default
    if not row["note"] and default and not annotation.get("reason"):
        row["note"] = case_annotation.get("note", "")  # the case note explains this default
    return row


def is_latest(verdict, args):
    _, admits, floor = verdict
    return floor if args.strict_ranges else admits


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def summarize(rows):
    valid = [r for r in rows if r["outcome"] != "absent"]
    al = sum(r["outcome"] == "already_latest" for r in valid)
    mit = sum(r["outcome"] == "mitigated" for r in valid)
    return len(valid), al, mit, len(valid) - al


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir", nargs="?", default=str(HERE / "claude-code-opus"))
    ap.add_argument("--cases", default=str(HERE / "cases_top.json"))
    ap.add_argument("--snapshot", default=str(HERE / "latest_versions_snapshot.json"))
    ap.add_argument("--annotations", default=None, help="default: <run_dir>/annotations.json")
    ap.add_argument("--strict-ranges", action="store_true",
                    help="a range counts as latest only if its lower bound is latest; floating tags never do")
    ap.add_argument("--no-substitutes", action="store_true", help="exclude reps that declare a substitute")
    ap.add_argument("--latex", action="store_true", help="also print the paper-table rows")
    ap.add_argument("--runs", action="store_true", help="also print every rep")
    ap.add_argument("--json-out", default=None)
    args = ap.parse_args()

    run_dir = Path(args.run_dir)
    cases, snapshot = load_targets(args.cases, args.snapshot)
    ann_path = Path(args.annotations) if args.annotations else run_dir / "annotations.json"
    annotations = json.loads(ann_path.read_text()) if ann_path.exists() else {}
    run_notes, case_notes = annotations.get("runs", {}), annotations.get("cases", {})

    rows = []
    for case_dir in sorted(p for p in run_dir.iterdir() if p.is_dir() and p.name in cases):
        for condition in ("nohook", "hook"):
            for rep_dir in sorted((case_dir / condition).glob("rep*")):
                key = f"{case_dir.name}/{condition}/{rep_dir.name}"
                rows.append(classify(cases[case_dir.name], condition, rep_dir, snapshot, args,
                                     run_notes.get(key, {}), case_notes.get(case_dir.name, {})))

    def of(cond, eco=None):
        return [r for r in rows if r["condition"] == cond and (eco is None or r["ecosystem"] == eco)]

    rule = "strict: range lower bound must be latest" if args.strict_ranges else "lenient: ranges admitting latest count"
    print("=" * 110)
    print(f"{run_dir.name} vs {Path(args.snapshot).name}   ({rule}; substitutes "
          f"{'excluded' if args.no_substitutes else 'judged against their own latest'})")
    print("=" * 110)

    # Paper table: per ecosystem, its tasks, then one sub-column per repetition
    # for Already latest (nohook), Already latest (hook) and Mitigated, each
    # x/y out of that repetition's valid reps (or stale candidates); Rate
    # pools Mitigated over the repetitions.
    reps = sorted({r["rep"] for r in rows})
    order = sorted(ECOSYSTEMS.values(), key=lambda e: e[1].lower())
    width = 7 * len(reps) - 1
    print(f"\n{'':16}|       | {'Nohook (RQ1)':{width}} | Hook (RQ2)")
    print(f"{'':16}|       | {'Already latest':{width}} | {'Already latest':{width}} | {'Mitigated':{width}} |")
    print(f"{'':16}| Tasks | " + " | ".join(" ".join(f"{rep:<6}" for rep in reps) for _ in range(3)) + " | Rate")
    latex = []
    for eco, label in order + [(None, "All")]:
        tasks = len({r["case"] for r in rows if eco is None or r["ecosystem"] == eco})
        if not tasks:
            continue
        nohook = [summarize([r for r in of("nohook", eco) if r["rep"] == rep]) for rep in reps]
        hook = [summarize([r for r in of("hook", eco) if r["rep"] == rep]) for rep in reps]
        _, _, h_mit, cand = summarize(of("hook", eco))
        rate = f"{h_mit}/{cand} ({100 * h_mit / cand:.0f}%)" if cand else f"{h_mit}/{cand} (n/a)"
        cells = ([f"{al}/{n}" for n, al, _, _ in nohook] + [f"{al}/{n}" for n, al, _, _ in hook]
                 + [f"{mit}/{c}" for _, _, mit, c in hook])
        groups = [cells[i:i + len(reps)] for i in range(0, len(cells), len(reps))]
        print(f"{label:16}| {tasks:<5} | " + " | ".join(" ".join(f"{c:<6}" for c in g) for g in groups) + f" | {rate}")
        # same column padding as the paper's table, "--" when no rep was stale
        tex_rate = rate.replace("%", "\\%").replace("(n/a)", "(--)")
        latex.append(f"    {label:<15}& {tasks:<3}& " + "& ".join(f"{c:<6}" for c in cells) + f"& {tex_rate} \\\\")
    if args.latex:
        print("\n" + "\n".join(latex))

    # pooled over repetitions, for the prose (e.g. 104/146)
    print(f"\nPooled over repetitions\n{'':16}| Nohook (RQ1)          | Hook (RQ2)")
    print(f"{'':16}| Valid  Already latest | Valid  Already latest  Mitigated  Rate")
    for eco, label in order + [(None, "All")]:
        n_valid, n_al, _, _ = summarize(of("nohook", eco))
        h_valid, h_al, h_mit, cand = summarize(of("hook", eco))
        if not n_valid and not h_valid:
            continue
        rate = f"{100 * h_mit / cand:.0f}%" if cand else "n/a"
        print(f"{label:16}| {n_valid:<6} {f'{n_al}/{n_valid}':<15}| {h_valid:<6} {f'{h_al}/{h_valid}':<15} "
              f"{f'{h_mit}/{cand}':<10} {rate}")

    newer = [r for r in rows if r["newer"]]
    print("\nSnapshot check: reps holding a release newer than the recorded latest "
          "(manifest, lockfiles, hook suggestions): " + ("none" if not newer else f"{len(newer)}"))
    for r in newer:
        print(f"  {r['case']}/{r['condition']}/{r['rep']}: " + "; ".join(r["newer"]))

    for cond, title in (("nohook", "RQ1 (nohook)"), ("hook", "RQ2 (hook)")):
        print(f"\n{title}: how valid reps ended")
        print(f"  {'ecosystem':15} {'latest via tool':>16} {'via memory':>11} {'mitigated':>10} {'stale':>6}  stale reasons")
        for eco, label in order + [(None, "All")]:
            sub = [r for r in of(cond, eco) if r["outcome"] != "absent"]
            if not sub:
                continue
            al = [r for r in sub if r["outcome"] == "already_latest"]
            stale = [r for r in sub if r["outcome"] == "stale"]
            reasons = Counter(r["reason"] for r in stale)
            print(f"  {label:15} {sum(r['route'] == 'tool' for r in al):>16} {sum(r['route'] != 'tool' for r in al):>11} "
                  f"{sum(r['outcome'] == 'mitigated' for r in sub):>10} {len(stale):>6}  "
                  + ", ".join(f"{k} {v}" for k, v in reasons.most_common()))

    print("\nReps not ending on latest")
    for r in rows:
        if r["outcome"] == "stale":
            print(f"  {r['case']}/{r['condition']}/{r['rep']}: {r['declared'] or r['target']} = {r['spec']} "
                  f"(latest {r['latest'] or '-'}) [{r['reason']}]")
            if r["note"]:
                print(f"      {r['note']}")

    mitigated = [r for r in rows if r["outcome"] == "mitigated"]
    firsts = Counter(r["first_route"] for r in mitigated)
    print(f"\nMitigated reps: {len(mitigated)} (rejected first write typed from memory {firsts['memory']}, "
          f"after a lookup {firsts['tool']})")
    for r in rows:
        if r["outcome"] == "mitigated":
            print(f"  {r['case']}/{r['rep']}: rejected {', '.join(r['rejected'])}; final {r['declared']} = {r['spec']}"
                  + (f" (first write from {r['first_route']})" if r["first_route"] else ""))
            if r["note"]:
                print(f"      {r['note']}")

    flagged = [r for r in rows if r["outcome"] == "already_latest" and r["condition"] == "hook" and r["rejected"]]
    if flagged:
        print("\nHook reps counted already latest despite a rejection naming the package (rejected pin already admitted latest)")
        for r in flagged:
            print(f"  {r['case']}/{r['rep']}: rejected {', '.join(r['rejected'])}; final {r['declared']} = {r['spec']}")

    for cond in ("nohook", "hook"):
        absent = [r for r in of(cond) if r["outcome"] == "absent"]
        print(f"\nExcluded, {cond}: {len(absent)} of {len(of(cond))} reps")
        for case_id in sorted({r["case"] for r in absent}):
            reps = [r for r in absent if r["case"] == case_id]
            reasons = Counter(r["reason"] for r in reps)
            print(f"  {case_id}: {', '.join(r['rep'] for r in reps)} ({', '.join(reasons)})")
            for note in dict.fromkeys(r["note"] for r in reps if r["note"]):
                print(f"      {note}")

    subs = [r for r in rows if r["substitute"]]
    if subs:
        print(f"\nSubstitutes judged in place of the target: {len(subs)} reps")
        by = defaultdict(list)
        for r in subs:
            by[(r["case"], r["target"], r["declared"])].append(f"{r['condition']}/{r['rep']}")
        for (case_id, target, name), reps in sorted(by.items()):
            print(f"  {case_id}: {target} -> {name} ({', '.join(reps)})")

    fallbacks = [r for r in rows if r["fallback_model"]]
    if fallbacks:
        print("\nReps partly answered by a fallback model (safeguard refusal)")
        for r in fallbacks:
            print(f"  {r['case']}/{r['condition']}/{r['rep']}: {r['fallback_model']}")

    print("\nPer case (valid reps)")
    print(f"  {'case':42} {'declared':34} {'nohook':>7} | {'hook al.':>8} {'mitig.':>7} {'final':>6}")
    for case_id in sorted(cases):
        n = [r for r in of("nohook") if r["case"] == case_id and r["outcome"] != "absent"]
        h = [r for r in of("hook") if r["case"] == case_id and r["outcome"] != "absent"]
        if not any(r["case"] == case_id for r in rows):
            continue
        names = sorted({r["declared"] for r in n + h if r["declared"]}) or ["-"]
        n_al = sum(r["outcome"] == "already_latest" for r in n)
        h_al = sum(r["outcome"] == "already_latest" for r in h)
        h_mit = sum(r["outcome"] == "mitigated" for r in h)
        print(f"  {case_id:42} {', '.join(names)[:34]:34} {f'{n_al}/{len(n)}':>7} | {f'{h_al}/{len(h)}':>8} "
              f"{f'{h_mit}/{len(h) - h_al}':>7} {f'{h_al + h_mit}/{len(h)}':>6}")

    noted = [(c, n["note"]) for c, n in sorted(case_notes.items()) if n.get("note")]
    if noted:
        print("\nCase notes (manual review)")
        for case_id, note in noted:
            print(f"  {case_id}: {note}")

    if args.runs:
        print("\nAll reps")
        for r in rows:
            print(f"  {r['case']:42} {r['condition']:6} {r['rep']} {str(r['declared']):34} {str(r['spec']):14} "
                  f"latest={str(r['latest']):10} {r['outcome']:14} route={r['route']} first={r['first_route']}"
                  + (f" rejected=[{'; '.join(r['rejected'])}]" if r["rejected"] else "")
                  + (f" reason={r['reason']}" if r["reason"] else ""))

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(rows, indent=2))
        print(f"\nWrote per-rep rows to {args.json_out}")


if __name__ == "__main__":
    main()
