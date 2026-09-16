package npm

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

func TestParsePackageJSONPins(t *testing.T) {
	content := `{
		"dependencies": {
			"runtime": "1.2.3",
			"alias": "npm:@scope/actual@8.0.0",
			"prerelease": "2.0.0-rc.1",
			"build": "3.0.0+metadata",
			"caret": "^4.0.0",
			"tilde": "~4.1.0",
			"minimum": ">=4.2.0",
			"bounded": ">=4.0.0 <5.0.0",
			"xrange": "4.x",
			"partial": "4",
			"or": "^4.0.0 || ^5.0.0",
			"tag": "latest",
			"workspace": "workspace:*",
			"file": "file:../local",
			"git": "git+https://github.com/example/repo.git"
		},
		"devDependencies": {
			"development": "5.0.0"
		},
		"optionalDependencies": {
			"optional": "6.0.0"
		},
		"peerDependencies": {
			"peer": "7.0.0"
		}
	}`

	got, err := parsePackageJSONPins(content)
	if err != nil {
		t.Fatalf("parsePackageJSONPins() error = %v", err)
	}

	want := map[string]pins.Spec{
		"dependencies/runtime":          {Version: "1.2.3"},
		"dependencies/alias":            {Version: "8.0.0"},
		"dependencies/prerelease":       {Version: "2.0.0-rc.1"},
		"dependencies/build":            {Version: "3.0.0+metadata"},
		"dependencies/caret":            {Operator: "^", Version: "4.0.0"},
		"dependencies/tilde":            {Operator: "~", Version: "4.1.0"},
		"dependencies/minimum":          {Operator: ">=", Version: "4.2.0"},
		"devDependencies/development":   {Version: "5.0.0"},
		"optionalDependencies/optional": {Version: "6.0.0"},
		"peerDependencies/peer":         {Version: "7.0.0"},
	}
	if len(got) != len(want) {
		t.Fatalf("parsePackageJSONPins() returned %d pins, want %d: %#v", len(got), len(want), got)
	}
	for location, spec := range want {
		if got[location].Operator != spec.Operator || got[location].Version != spec.Version {
			t.Errorf("parsePackageJSONPins()[%q] = %q %q, want %q %q", location, got[location].Operator, got[location].Version, spec.Operator, spec.Version)
		}
	}
	if pin := got["dependencies/alias"]; pin.Name != "@scope/actual" || pin.PURL != "pkg:npm/%40scope/actual" {
		t.Errorf("alias pin = %#v, want canonical target package", pin)
	}
}

func TestParsePackageJSONPinsEmptyAndInvalid(t *testing.T) {
	got, err := parsePackageJSONPins(" \n")
	if err != nil {
		t.Fatalf("parsePackageJSONPins(empty) error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("parsePackageJSONPins(empty) = %#v, want no pins", got)
	}

	if _, err := parsePackageJSONPins("{"); err == nil {
		t.Fatal("parsePackageJSONPins(invalid) returned nil error")
	}
}

func TestCheckPackageJSONOnlyChecksChangedPins(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:npm/added": "2.0.0"}}

	before := `{"dependencies":{"existing":"1.0.0","range":"^1.0.0"}}`
	after := `{"dependencies":{"existing":"1.0.0","added":"1.0.0","range":"^1.0.0","bounded":">=1.0.0 <2.0.0"}}`

	got, err := CheckPackageJSON(before, after, res)
	if err != nil {
		t.Fatalf("CheckPackageJSON() error = %v", err)
	}
	if res.lookups != 1 {
		t.Fatalf("CheckPackageJSON() made %d resolver lookups, want 1", res.lookups)
	}
	if len(got) != 1 {
		t.Fatalf("CheckPackageJSON() returned %d mismatches, want 1: %#v", len(got), got)
	}
	if got[0].Name != "added" || got[0].Current != "1.0.0" || got[0].Latest != "2.0.0" {
		t.Fatalf("CheckPackageJSON() mismatch = %#v", got[0])
	}
}

// TestCheckPackageJSONRangeIsBumpedInPlace covers chains-project/yul#43: a
// caret range like "^0.1.0" still resolves to whatever the build tool
// picks later, but yul wants the manifest itself to name the latest
// version, so the base version is bumped while the operator is kept.
func TestCheckPackageJSONRangeIsBumpedInPlace(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{
		"pkg:npm/caret":   "0.5.1",
		"pkg:npm/tilde":   "1.4.2",
		"pkg:npm/minimum": "3.0.0",
		"pkg:npm/current": "2.0.0",
	}}

	before := `{}`
	after := `{"dependencies":{"caret":"^0.1.0","tilde":"~1.2.0","minimum":">=2.0.0","current":"^2.0.0"}}`

	got, err := CheckPackageJSON(before, after, res)
	if err != nil {
		t.Fatalf("CheckPackageJSON() error = %v", err)
	}
	want := map[string][2]string{
		"caret":   {"^0.1.0", "^0.5.1"},
		"tilde":   {"~1.2.0", "~1.4.2"},
		"minimum": {">=2.0.0", ">=3.0.0"},
	}
	if len(got) != len(want) {
		t.Fatalf("CheckPackageJSON() returned %d mismatches, want %d: %#v", len(got), len(want), got)
	}
	for _, m := range got {
		w, ok := want[m.Name]
		if !ok || m.Current != w[0] || m.Latest != w[1] {
			t.Errorf("CheckPackageJSON() mismatch for %s = %q -> %q, want %q -> %q", m.Name, m.Current, m.Latest, w[0], w[1])
		}
	}
}

func TestCheckPackageJSONScopedPackage(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:npm/%40scope/pkg": "2.0.0"}}

	before := `{}`
	after := `{"dependencies":{"@scope/pkg":"1.0.0"}}`

	got, err := CheckPackageJSON(before, after, res)
	if err != nil {
		t.Fatalf("CheckPackageJSON() error = %v", err)
	}
	if len(got) != 1 || got[0].Name != "@scope/pkg" {
		t.Fatalf("CheckPackageJSON() = %#v, want one mismatch for @scope/pkg", got)
	}
}
