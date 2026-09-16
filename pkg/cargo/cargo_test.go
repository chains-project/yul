package cargo

import (
	"context"
	"testing"

	"github.com/chains-project/yul/pkg/util/pins"
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
minimum = ">=1.2.3"
wildcard = "*"
partial-wildcard = "1.*"
multi = ">=1.2, <1.5"
table-exact = { version = "=2.0.0" }
local = { path = "../local" }
workspace-dep = { workspace = true }

[dev-dependencies]
exact = "=9.9.9"
`

	got, err := parseCargoPins(content)
	if err != nil {
		t.Fatalf("parseCargoPins() error = %v", err)
	}

	want := map[string]pins.Pin{
		"runtime/exact":          {Operator: "=", Version: "1.2.3"},
		"runtime/caret":          {Version: "1.2.3"},
		"runtime/explicit-caret": {Operator: "^", Version: "1.2.3"},
		"runtime/tilde":          {Operator: "~", Version: "1.2.3"},
		"runtime/minimum":        {Operator: ">=", Version: "1.2.3"},
		"runtime/table-exact":    {Operator: "=", Version: "2.0.0"},
		"development/exact":      {Operator: "=", Version: "9.9.9"},
	}
	if len(got) != len(want) {
		t.Fatalf("parseCargoPins() returned %d pins, want %d: %#v", len(got), len(want), got)
	}
	for location, spec := range want {
		pin, ok := got[location]
		if !ok {
			t.Errorf("parseCargoPins() missing %q", location)
			continue
		}
		if pin.Operator != spec.Operator || pin.Version != spec.Version {
			t.Errorf("parseCargoPins()[%q] = %q %q, want %q %q", location, pin.Operator, pin.Version, spec.Operator, spec.Version)
		}
		if pin.PURL == "" {
			t.Errorf("parseCargoPins()[%q].PURL is empty", location)
		}
	}
}

func TestParseCargoPinsEmptyAndInvalid(t *testing.T) {
	got, err := parseCargoPins(" \n")
	if err != nil {
		t.Fatalf("parseCargoPins(empty) error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("parseCargoPins(empty) = %#v, want no pins", got)
	}

	got, err = parseCargoPins("[package]\nname = \"demo\"\nversion = \"0.1.0\"\n")
	if err != nil {
		t.Fatalf("parseCargoPins(no deps) error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("parseCargoPins(no deps) = %#v, want no pins", got)
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
	if got[0].Name != "added" || got[0].Current != "=1.0.0" || got[0].Latest != "=2.0.0" {
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

// TestCheckCargoTomlRangesAreBumpedInPlace covers chains-project/yul#43: a
// bare version like "1.0.107" is Cargo's implicit caret range, so it isn't
// an exact pin, but the manifest should still name the latest version. The
// base version is bumped and the requirement's shape (bare, "^", "~",
// ">=", "=") is preserved in the suggestion.
func TestCheckCargoTomlRangesAreBumpedInPlace(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{
		"pkg:cargo/proc-macro2": "1.0.110",
		"pkg:cargo/quote":       "1.0.50",
		"pkg:cargo/syn":         "3.1.0",
		"pkg:cargo/minimum":     "2.0.0",
		"pkg:cargo/current":     "1.0.0",
	}}

	before := `[dependencies]
`
	after := `[dependencies]
proc-macro2 = "1.0.107"
quote = "^1.0.47"
syn = { version = "~3.0.5", features = ["full"] }
minimum = ">=1.0.0"
current = "1.0.0"
`

	got, err := CheckCargoToml(before, after, res)
	if err != nil {
		t.Fatalf("CheckCargoToml() error = %v", err)
	}
	want := map[string][2]string{
		"proc-macro2": {"1.0.107", "1.0.110"},
		"quote":       {"^1.0.47", "^1.0.50"},
		"syn":         {"~3.0.5", "~3.1.0"},
		"minimum":     {">=1.0.0", ">=2.0.0"},
	}
	if len(got) != len(want) {
		t.Fatalf("CheckCargoToml() returned %d mismatches, want %d: %#v", len(got), len(want), got)
	}
	for _, m := range got {
		w, ok := want[m.Name]
		if !ok || m.Current != w[0] || m.Latest != w[1] {
			t.Errorf("CheckCargoToml() mismatch for %s = %q -> %q, want %q -> %q", m.Name, m.Current, m.Latest, w[0], w[1])
		}
	}
}

// TestCheckCargoTomlWildcardsAreLeftAlone: "*" and "1.*" have no single
// base version to bump, and multi-clause ranges would need both bounds
// rewritten, so none of them are looked up.
func TestCheckCargoTomlWildcardsAreLeftAlone(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{}}

	after := `[dependencies]
any = "*"
minor = "1.*"
bounded = ">=1.2, <1.5"
`

	got, err := CheckCargoToml("", after, res)
	if err != nil {
		t.Fatalf("CheckCargoToml() error = %v", err)
	}
	if res.lookups != 0 {
		t.Fatalf("CheckCargoToml() made %d resolver lookups, want 0", res.lookups)
	}
	if len(got) != 0 {
		t.Fatalf("CheckCargoToml() = %#v, want no mismatches", got)
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
