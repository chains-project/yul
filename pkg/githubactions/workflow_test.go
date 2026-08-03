package githubactions

import (
	"context"
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
		{path: "/repo/.github/workflows/ci.yml", want: true},
		{path: "/repo/.github/workflows/release.yaml", want: true},
		{path: ".github/workflows/ci.yml", want: true},
		{path: "workflow.yml", want: true}, // git-pkgs/manifests' own testing fallback
		{path: "/repo/action.yml", want: false},
		{path: "/repo/package.json", want: false},
		{path: "/repo/.github/dependabot.yml", want: false},
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
      - uses: actions/checkout@a1b2c3d4e5f60718293a4b5c6d7e8f9012345678
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

func TestCheckWorkflowFreshPinBelowLatest(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:githubactions/actions/checkout": "v4.2.1"}}

	before := ""
	after := "jobs:\n  build:\n    steps:\n      - uses: actions/checkout@v4\n"

	got, err := CheckWorkflow(before, after, res)
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

	got, err := CheckWorkflow(before, after, res)
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

	got, err := CheckWorkflow(before, after, res)
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

	got, err := CheckWorkflow(before, after, res)
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

	got, err := CheckWorkflow(before, after, res)
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

	if _, err := CheckWorkflow(before, after, res); err == nil {
		t.Fatal("CheckWorkflow() returned nil error, want an error for an unresolved action")
	}
}
