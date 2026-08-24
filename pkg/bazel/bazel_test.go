package bazel

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

func (r *fakeResolver) LatestVersions(_ context.Context, purls []string) (map[string]string, error) {
	r.lookups++
	result := make(map[string]string, len(purls))
	for _, purl := range purls {
		if v, ok := r.latest[purl]; ok {
			result[purl] = v
		}
	}
	return result, nil
}

func TestParseModuleBazelPins(t *testing.T) {
	content := `
module(name = "demo", version = "1.0.0")

bazel_dep(name = "rules_go", version = "0.41.0")
bazel_dep(name = "google_benchmark", version = "1.9.4", dev_dependency = True)
`

	got, err := parseModuleBazelPins(content)
	if err != nil {
		t.Fatalf("parseModuleBazelPins() error = %v", err)
	}

	want := map[string]string{
		"rules_go":         "0.41.0",
		"google_benchmark": "1.9.4",
	}
	if len(got) != len(want) {
		t.Fatalf("parseModuleBazelPins() returned %d pins, want %d: %#v", len(got), len(want), got)
	}
	for name, version := range want {
		pin, ok := got[name]
		if !ok {
			t.Errorf("parseModuleBazelPins() missing %q", name)
			continue
		}
		if pin.Version != version {
			t.Errorf("parseModuleBazelPins()[%q].Version = %q, want %q", name, pin.Version, version)
		}
		if pin.PURL == "" {
			t.Errorf("parseModuleBazelPins()[%q].PURL is empty", name)
		}
	}
}

func TestParseModuleBazelPinsEmptyAndInvalid(t *testing.T) {
	got, err := parseModuleBazelPins(" \n")
	if err != nil {
		t.Fatalf("parseModuleBazelPins(empty) error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("parseModuleBazelPins(empty) = %#v, want no pins", got)
	}

	got, err = parseModuleBazelPins(`module(name = "demo", version = "1.0.0")` + "\n")
	if err != nil {
		t.Fatalf("parseModuleBazelPins(no deps) error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("parseModuleBazelPins(no deps) = %#v, want no pins", got)
	}
}

func TestCheckModuleBazelOnlyChecksChangedDeps(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:bazel/added": "2.0.0"}}

	before := `bazel_dep(name = "existing", version = "1.0.0")
`
	after := `bazel_dep(name = "existing", version = "1.0.0")
bazel_dep(name = "added", version = "1.0.0")
`

	got, err := CheckModuleBazel(before, after, res)
	if err != nil {
		t.Fatalf("CheckModuleBazel() error = %v", err)
	}
	if res.lookups != 1 {
		t.Fatalf("CheckModuleBazel() made %d resolver lookups, want 1", res.lookups)
	}
	if len(got) != 1 {
		t.Fatalf("CheckModuleBazel() returned %d mismatches, want 1: %#v", len(got), got)
	}
	if got[0].Name != "added" || got[0].Current != "1.0.0" || got[0].Latest != "2.0.0" {
		t.Fatalf("CheckModuleBazel() mismatch = %#v", got[0])
	}
}

func TestCheckModuleBazelAtLatestNoMismatch(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:bazel/added": "1.0.0"}}

	before := ""
	after := `bazel_dep(name = "added", version = "1.0.0")
`

	got, err := CheckModuleBazel(before, after, res)
	if err != nil {
		t.Fatalf("CheckModuleBazel() error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("CheckModuleBazel() = %#v, want no mismatches", got)
	}
}

func TestCheckModuleBazelDevDependencyChecked(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:bazel/added": "2.0.0"}}

	before := ""
	after := `bazel_dep(name = "added", version = "1.0.0", dev_dependency = True)
`

	got, err := CheckModuleBazel(before, after, res)
	if err != nil {
		t.Fatalf("CheckModuleBazel() error = %v", err)
	}
	if len(got) != 1 {
		t.Fatalf("CheckModuleBazel() returned %d mismatches, want 1: %#v", len(got), got)
	}
	if got[0].Name != "added" || got[0].Latest != "2.0.0" {
		t.Fatalf("CheckModuleBazel() mismatch = %#v", got[0])
	}
}

func TestCheckModuleBazelUntouchedDepIgnored(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:bazel/other": "9.0.0"}}

	before := `bazel_dep(name = "other", version = "1.0.0")
`
	after := `bazel_dep(name = "other", version = "1.0.0")
bazel_dep(name = "added", version = "1.0.0")
`
	res.latest["pkg:bazel/added"] = "1.0.0"

	got, err := CheckModuleBazel(before, after, res)
	if err != nil {
		t.Fatalf("CheckModuleBazel() error = %v", err)
	}
	// "other" is outdated (1.0.0 vs latest 9.0.0) but untouched by the
	// write, so only "added" should ever get looked up.
	if res.lookups != 1 {
		t.Fatalf("CheckModuleBazel() made %d resolver lookups, want 1", res.lookups)
	}
	if len(got) != 0 {
		t.Fatalf("CheckModuleBazel() = %#v, want no mismatches", got)
	}
}
