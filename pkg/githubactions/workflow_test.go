package githubactions

import (
	"context"
	"fmt"
	"testing"
)

// fakeResolver resolves latest versions from a fixed PURL->version map, so
// tests don't make real network requests.
type fakeResolver struct {
	latest  map[string]string
	lookups int
}

func (r *fakeResolver) LatestVersions(ctx context.Context, purls []string) (map[string]string, error) {
	r.lookups++
	result := make(map[string]string, len(purls))
	for _, purl := range purls {
		if v, ok := r.latest[purl]; ok {
			result[purl] = v
		}
	}
	return result, nil
}

func TestCheckerMatchesPath(t *testing.T) {
	tests := []struct {
		path string
		want bool
	}{
		{path: ".github/workflows/ci.yml", want: true},
		{path: ".github/workflows/release.yaml", want: true},
		{path: "/home/user/project/.github/workflows/ci.yml", want: true}, // hook file_paths are typically absolute
		{path: "workflow.yml", want: true},                                // git-pkgs/manifests' own testing fallback
		{path: "action.yml", want: false},
		{path: "package.json", want: false},
		{path: ".github/dependabot.yml", want: false},
	}

	c := Checker{}
	for _, test := range tests {
		t.Run(test.path, func(t *testing.T) {
			if got := c.MatchesPath(test.path); got != test.want {
				t.Errorf("MatchesPath(%q) = %v, want %v", test.path, got, test.want)
			}
		})
	}
}

func TestParseWorkflowPins(t *testing.T) {
	content := `
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/cache/restore@v3
      - uses: actions/setup-node@a1b2c3d4e5f60718293a4b5c6d7e8f9012345678 # v4.1.0
      - uses: step-security/harden-runner@1234567890abcdef1234567890abcdef12345678 # not-a-version
      - uses: some-org/bare-sha-action@deadbeefcafef00dfeedfacefeedfacefeedface
      - uses: my-org/local-branch-action@main
      - uses: ./local-action
      - uses: docker://alpine:3.19
    container: node:20
    services:
      redis:
        image: redis:7
`
	got, err := parseWorkflowPins(content)
	if err != nil {
		t.Fatalf("parseWorkflowPins() error = %v", err)
	}

	want := map[string]string{
		"actions/checkout":      "v4",
		"actions/cache/restore": "v3",
		"actions/setup-node":    "v4.1.0", // SHA pin, version recovered from its trailing comment
	}
	if len(got) != len(want) {
		t.Fatalf("parseWorkflowPins() = %#v, want %d pins: %#v", got, len(want), want)
	}
	for name, version := range want {
		if got[name].version != version {
			t.Errorf("parseWorkflowPins()[%q].version = %q, want %q", name, got[name].version, version)
		}
	}
}

func TestParseWorkflowPinsEmptyAndInvalid(t *testing.T) {
	got, err := parseWorkflowPins(" \n")
	if err != nil {
		t.Fatalf("parseWorkflowPins(empty) error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("parseWorkflowPins(empty) = %#v, want no pins", got)
	}

	if _, err := parseWorkflowPins("jobs: [this is not a map"); err == nil {
		t.Fatal("parseWorkflowPins(invalid) returned nil error")
	}
}

func TestParseShaComments(t *testing.T) {
	content := "" +
		"      - uses: actions/checkout@a1b2c3d4e5f60718293a4b5c6d7e8f9012345678 # v4.2.1\n" +
		"      - uses: actions/setup-node@1234567890abcdef1234567890abcdef12345678 # pinned, see SECURITY.md\n" +
		"      - uses: actions/cache@deadbeefcafef00dfeedfacefeedfacefeedface\n" + // no comment at all
		"      - uses: my-org/tagged-action@v2 # redundant comment on an already-tagged pin\n"

	got := parseShaComments(content)

	want := map[string]string{
		"actions/checkout": "v4.2.1",
	}
	if len(got) != len(want) {
		t.Fatalf("parseShaComments() = %#v, want %#v", got, want)
	}
	for name, tag := range want {
		if got[name] != tag {
			t.Errorf("parseShaComments()[%q] = %q, want %q", name, got[name], tag)
		}
	}
}

func TestCheckWorkflowShaCommentPinBelowLatest(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:githubactions/actions/checkout": "v4.2.1"}}

	before := ""
	after := "jobs:\n  build:\n    steps:\n      - uses: actions/checkout@a1b2c3d4e5f60718293a4b5c6d7e8f9012345678 # v4.0.0\n"

	got, err := CheckWorkflow(before, after, res, nil)
	if err != nil {
		t.Fatalf("CheckWorkflow() error = %v", err)
	}
	if len(got) != 1 {
		t.Fatalf("CheckWorkflow() = %#v, want 1 mismatch", got)
	}
	if got[0].Name != "actions/checkout" || got[0].Current != "v4.0.0" || got[0].Latest != "v4.2.1" {
		t.Fatalf("CheckWorkflow() mismatch = %#v", got[0])
	}
}

func TestCheckWorkflowFreshPinBelowLatest(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:githubactions/actions/checkout": "v4.2.1"}}

	before := ""
	after := "jobs:\n  build:\n    steps:\n      - uses: actions/checkout@v4\n"

	got, err := CheckWorkflow(before, after, res, nil)
	if err != nil {
		t.Fatalf("CheckWorkflow() error = %v", err)
	}
	if res.lookups != 1 {
		t.Fatalf("CheckWorkflow() made %d resolver lookups, want 1", res.lookups)
	}
	if len(got) != 1 {
		t.Fatalf("CheckWorkflow() = %#v, want 1 mismatch", got)
	}
	if got[0].Name != "actions/checkout" || got[0].Current != "v4" || got[0].Latest != "v4.2.1" {
		t.Fatalf("CheckWorkflow() mismatch = %#v", got[0])
	}
}

func TestCheckWorkflowFreshPinAtLatest(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:githubactions/actions/checkout": "v4"}}

	before := ""
	after := "jobs:\n  build:\n    steps:\n      - uses: actions/checkout@v4\n"

	got, err := CheckWorkflow(before, after, res, nil)
	if err != nil {
		t.Fatalf("CheckWorkflow() error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("CheckWorkflow() = %#v, want no mismatches for an up-to-date pin", got)
	}
}

func TestCheckWorkflowIgnoresShaAndBranchPins(t *testing.T) {
	// A resolver with no entries: if the checker tried to resolve either of
	// these, Diff-style "no latest version found" handling would surface as
	// an error. No error and no mismatches means both were correctly
	// skipped before ever reaching the resolver.
	res := &fakeResolver{latest: map[string]string{}}

	before := ""
	after := "jobs:\n  build:\n    steps:\n      - uses: actions/checkout@a1b2c3d4e5f60718293a4b5c6d7e8f9012345678\n      - uses: actions/checkout@main\n"

	got, err := CheckWorkflow(before, after, res, nil)
	if err != nil {
		t.Fatalf("CheckWorkflow() error = %v", err)
	}
	if res.lookups != 0 {
		t.Fatalf("CheckWorkflow() made %d resolver lookups, want 0", res.lookups)
	}
	if len(got) != 0 {
		t.Fatalf("CheckWorkflow() = %#v, want no mismatches for SHA/branch pins", got)
	}
}

func TestCheckWorkflowSkipsUntouchedStep(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:githubactions/actions/setup-node": "v5.0.0"}}

	before := "jobs:\n  build:\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/setup-node@v4\n"
	after := "jobs:\n  build:\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/setup-node@v4\n      - run: echo hi\n"

	got, err := CheckWorkflow(before, after, res, nil)
	if err != nil {
		t.Fatalf("CheckWorkflow() error = %v", err)
	}
	if res.lookups != 0 {
		t.Fatalf("CheckWorkflow() made %d resolver lookups, want 0 for an edit that didn't touch a uses: pin", res.lookups)
	}
	if len(got) != 0 {
		t.Fatalf("CheckWorkflow() = %#v, want no mismatches", got)
	}
}

func TestCheckWorkflowReportsChangedPin(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:githubactions/actions/checkout": "v4"}}

	before := "jobs:\n  build:\n    steps:\n      - uses: actions/checkout@v3\n"
	after := "jobs:\n  build:\n    steps:\n      - uses: actions/checkout@v3.5.0\n"

	got, err := CheckWorkflow(before, after, res, nil)
	if err != nil {
		t.Fatalf("CheckWorkflow() error = %v", err)
	}
	if len(got) != 1 {
		t.Fatalf("CheckWorkflow() = %#v, want 1 mismatch", got)
	}
	if got[0].Current != "v3.5.0" || got[0].Latest != "v4" {
		t.Fatalf("CheckWorkflow() mismatch = %#v", got[0])
	}
}

func TestCheckWorkflowFailsOpenOnUnresolvedAction(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{}}

	before := ""
	after := "jobs:\n  build:\n    steps:\n      - uses: some-org/unlisted-action@v1\n"

	if _, err := CheckWorkflow(before, after, res, nil); err == nil {
		t.Fatal("CheckWorkflow() returned nil error, want an error for an unresolved action")
	}
}

// fakeShaResolver resolves SHAs from a fixed "repo@tag" -> sha map, or
// returns an error if err is set (to exercise the fail-open path).
type fakeShaResolver struct {
	sha map[string]string
	err error
}

func (r *fakeShaResolver) ResolveSHA(ctx context.Context, repo, tag string) (string, error) {
	if r.err != nil {
		return "", r.err
	}
	sha, ok := r.sha[repo+"@"+tag]
	if !ok {
		return "", fmt.Errorf("no sha for %s@%s", repo, tag)
	}
	return sha, nil
}

func TestCheckWorkflowSuggestsShaPin(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:githubactions/actions/cache": "v4.2.1"}}
	sha := &fakeShaResolver{sha: map[string]string{
		"actions/cache@v4.2.1": "8e8c483db84b4bee98b60c0593521ed34d9990e8",
	}}

	before := ""
	// A subpath action ("actions/cache/restore") - repoOf must strip the
	// subpath down to "actions/cache" before asking the SHA resolver.
	after := "jobs:\n  build:\n    steps:\n      - uses: actions/cache/restore@v4\n"

	got, err := CheckWorkflow(before, after, res, sha)
	if err != nil {
		t.Fatalf("CheckWorkflow() error = %v", err)
	}
	if len(got) != 1 {
		t.Fatalf("CheckWorkflow() = %#v, want 1 mismatch", got)
	}
	want := "8e8c483db84b4bee98b60c0593521ed34d9990e8 # v4.2.1"
	if got[0].Suggested != want {
		t.Errorf("CheckWorkflow() Suggested = %q, want %q", got[0].Suggested, want)
	}
	if got[0].Latest != "v4.2.1" {
		t.Errorf("CheckWorkflow() Latest = %q, want %q (unchanged even though Suggested is set)", got[0].Latest, "v4.2.1")
	}
}

func TestCheckWorkflowShaLookupFailsOpen(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:githubactions/actions/checkout": "v4.2.1"}}
	sha := &fakeShaResolver{err: fmt.Errorf("network error")}

	before := ""
	after := "jobs:\n  build:\n    steps:\n      - uses: actions/checkout@v4\n"

	got, err := CheckWorkflow(before, after, res, sha)
	if err != nil {
		t.Fatalf("CheckWorkflow() error = %v, want nil (SHA lookup failures shouldn't fail the check)", err)
	}
	if len(got) != 1 {
		t.Fatalf("CheckWorkflow() = %#v, want 1 mismatch", got)
	}
	if got[0].Suggested != "" {
		t.Errorf("CheckWorkflow() Suggested = %q, want empty on a failed SHA lookup", got[0].Suggested)
	}
	if got[0].Latest != "v4.2.1" {
		t.Errorf("CheckWorkflow() Latest = %q, want %q", got[0].Latest, "v4.2.1")
	}
}

func TestRepoOf(t *testing.T) {
	tests := []struct {
		name string
		want string
	}{
		{"actions/checkout", "actions/checkout"},
		{"actions/cache/restore", "actions/cache"},
		{"actions/cache/save", "actions/cache"},
		{"single-name", "single-name"},
	}
	for _, test := range tests {
		if got := repoOf(test.name); got != test.want {
			t.Errorf("repoOf(%q) = %q, want %q", test.name, got, test.want)
		}
	}
}
