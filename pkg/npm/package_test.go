package npm

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

func TestParsePackageJSONPins(t *testing.T) {
	content := `{
		"dependencies": {
			"runtime": "1.2.3",
			"alias": "npm:@scope/actual@8.0.0",
			"prerelease": "2.0.0-rc.1",
			"build": "3.0.0+metadata",
			"range": "^4.0.0",
			"tag": "latest",
			"workspace": "workspace:*"
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

	want := map[string]string{
		"dependencies/runtime":          "1.2.3",
		"dependencies/alias":            "8.0.0",
		"dependencies/prerelease":       "2.0.0-rc.1",
		"dependencies/build":            "3.0.0+metadata",
		"devDependencies/development":   "5.0.0",
		"optionalDependencies/optional": "6.0.0",
		"peerDependencies/peer":         "7.0.0",
	}
	if len(got) != len(want) {
		t.Fatalf("parsePackageJSONPins() returned %d pins, want %d: %#v", len(got), len(want), got)
	}
	for location, version := range want {
		if got[location].Version != version {
			t.Errorf("parsePackageJSONPins()[%q].Version = %q, want %q", location, got[location].Version, version)
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

func TestCheckPackageJSONOnlyChecksChangedExactPins(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:npm/added": "2.0.0"}}

	before := `{"dependencies":{"existing":"1.0.0"}}`
	after := `{"dependencies":{"existing":"1.0.0","added":"1.0.0","range":"^1.0.0"}}`

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
