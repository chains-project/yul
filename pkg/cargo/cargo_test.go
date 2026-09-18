package cargo

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

func TestParseCargoPins(t *testing.T) {
	content := `
[package]
name = "demo"
version = "0.1.0"

[dependencies]
exact = "=1.2.3"
caret = "1.2.3"
explicit-caret = "^1.2.3"
tilde = "~1.2.3"
wildcard = "*"
table-exact = { version = "=2.0.0" }
local = { path = "../local" }
workspace-dep = { workspace = true }

[dev-dependencies]
exact = "=9.9.9"
`

	got, err := parseCargo(content)
	if err != nil {
		t.Fatalf("parseCargo() error = %v", err)
	}

	want := map[string]string{
		"runtime/exact":       "1.2.3",
		"runtime/table-exact": "2.0.0",
		"development/exact":   "9.9.9",
	}
	for location, version := range want {
		pin, ok := got[location]
		if !ok {
			t.Errorf("parseCargo() missing %q", location)
			continue
		}
		if pin.Spec != version || pin.Range {
			t.Errorf("parseCargo()[%q] = %#v, want exact %q", location, pin, version)
		}
		if pin.PURL == "" {
			t.Errorf("parseCargo()[%q].PURL is empty", location)
		}
	}
}

// TestParseCargoRangesExcludesWildcard checks a bare "*" is never flagged
// since it can also mean a workspace-inherited dependency.
func TestParseCargoRangesExcludesWildcard(t *testing.T) {
	content := `
[dependencies]
caret = "1.2.3"
explicit-caret = "^1.2.3"
tilde = "~1.2.3"
wildcard = "*"
exact = "=1.2.3"
workspace-dep = { workspace = true }
`

	got, err := parseCargo(content)
	if err != nil {
		t.Fatalf("parseCargo() error = %v", err)
	}

	want := map[string]string{
		"runtime/caret":          "1.2.3",
		"runtime/explicit-caret": "^1.2.3",
		"runtime/tilde":          "~1.2.3",
	}
	for location, spec := range want {
		if got[location].Spec != spec || !got[location].Range {
			t.Errorf("parseCargo()[%q] = %#v, want range %q", location, got[location], spec)
		}
	}
	if _, ok := got["runtime/wildcard"]; ok {
		t.Errorf("parseCargo() = %#v, want bare \"*\" excluded", got)
	}
}

func TestParseCargoPinsEmptyAndInvalid(t *testing.T) {
	got, err := parseCargo(" \n")
	if err != nil {
		t.Fatalf("parseCargo(empty) error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("parseCargo(empty) = %#v, want no pins", got)
	}

	got, err = parseCargo("[package]\nname = \"demo\"\nversion = \"0.1.0\"\n")
	if err != nil {
		t.Fatalf("parseCargo(no deps) error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("parseCargo(no deps) = %#v, want no pins", got)
	}
}

func TestCheckCargoTomlOnlyChecksChangedDependencies(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:cargo/added": "2.0.0"}}

	before := `[dependencies]
existing = "=1.0.0"
`
	after := `[dependencies]
existing = "=1.0.0"
added = "=1.0.0"
`

	got, err := CheckCargoToml(before, after, res)
	if err != nil {
		t.Fatalf("CheckCargoToml() error = %v", err)
	}
	if res.lookups != 1 {
		t.Fatalf("CheckCargoToml() made %d resolver lookups, want 1", res.lookups)
	}
	if len(got) != 1 {
		t.Fatalf("CheckCargoToml() returned %d mismatches, want 1: %#v", len(got), got)
	}
	if got[0].Name != "added" || got[0].Current != "1.0.0" || got[0].Latest != "2.0.0" {
		t.Fatalf("CheckCargoToml() mismatch = %#v", got[0])
	}
}

func TestCheckCargoTomlAtLatestNoMismatch(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:cargo/added": "1.0.0"}}

	before := `[dependencies]
`
	after := `[dependencies]
added = "=1.0.0"
`

	got, err := CheckCargoToml(before, after, res)
	if err != nil {
		t.Fatalf("CheckCargoToml() error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("CheckCargoToml() = %#v, want no mismatches", got)
	}
}

// TestCheckCargoTomlBareVersionIsCaretRangeNotExact checks a bare version
// is flagged as a range recommendation, never as an outdated exact pin.
func TestCheckCargoTomlBareVersionIsCaretRangeNotExact(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:cargo/added": "9.0.0"}}

	before := `[dependencies]
`
	after := `[dependencies]
added = "1.0.0"
`

	got, err := CheckCargoToml(before, after, res)
	if err != nil {
		t.Fatalf("CheckCargoToml() error = %v", err)
	}
	if len(got) != 1 || !got[0].Range || got[0].Current != "1.0.0" || got[0].Suggested != "=9.0.0" {
		t.Fatalf("CheckCargoToml() = %#v, want a single range recommendation for the bare (caret) version", got)
	}
}

func TestCheckCargoTomlUntouchedDependencyIgnored(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:cargo/other": "9.0.0"}}

	before := `[dependencies]
other = "=1.0.0"
`
	after := `[dependencies]
other = "=1.0.0"
added = "=1.0.0"
`
	res.latest["pkg:cargo/added"] = "1.0.0"

	got, err := CheckCargoToml(before, after, res)
	if err != nil {
		t.Fatalf("CheckCargoToml() error = %v", err)
	}
	// "other" is outdated (=1.0.0 vs latest 9.0.0) but untouched by the
	// write, so only "added" should ever get looked up.
	if res.lookups != 1 {
		t.Fatalf("CheckCargoToml() made %d resolver lookups, want 1", res.lookups)
	}
	if len(got) != 0 {
		t.Fatalf("CheckCargoToml() = %#v, want no mismatches", got)
	}
}

func TestCheckCargoTomlSameCrateDifferentSectionsAreIndependentPins(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:cargo/dual": "2.0.0"}}

	before := `[dependencies]
dual = "=1.0.0"

[dev-dependencies]
dual = "=1.0.0"
`
	after := `[dependencies]
dual = "=1.0.0"

[dev-dependencies]
dual = "=1.0.0"
`

	got, err := CheckCargoToml(before, after, res)
	if err != nil {
		t.Fatalf("CheckCargoToml() error = %v", err)
	}
	if res.lookups != 0 {
		t.Fatalf("CheckCargoToml() made %d resolver lookups, want 0 (nothing changed)", res.lookups)
	}
	if len(got) != 0 {
		t.Fatalf("CheckCargoToml() = %#v, want no mismatches for an untouched write", got)
	}
}
