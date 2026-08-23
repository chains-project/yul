package golang

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

func TestParseGoModPinsCollectsRequireEntries(t *testing.T) {
	content := `module example.com/demo

go 1.21

require github.com/stretchr/testify v1.8.4

require (
	github.com/pkg/errors v0.9.1
	golang.org/x/text v0.14.0 // indirect
	golang.org/x/sync v0.0.0-20210220032951-036812b2e83c
)

replace github.com/pkg/errors => github.com/pkg/errors v0.8.0
`

	got, err := parseGoModPins(content)
	if err != nil {
		t.Fatalf("parseGoModPins() error = %v", err)
	}

	want := map[string]string{
		"github.com/stretchr/testify": "v1.8.4",
		"github.com/pkg/errors":       "v0.9.1", // the require line, not the replace directive
		"golang.org/x/text":           "v0.14.0",
		"golang.org/x/sync":           "v0.0.0-20210220032951-036812b2e83c",
	}
	if len(got) != len(want) {
		t.Fatalf("parseGoModPins() returned %d pins, want %d: %#v", len(got), len(want), got)
	}
	for name, version := range want {
		pin, ok := got[name]
		if !ok {
			t.Errorf("parseGoModPins() missing %q", name)
			continue
		}
		if pin.Version != version {
			t.Errorf("parseGoModPins()[%q].Version = %q, want %q", name, pin.Version, version)
		}
		if pin.PURL == "" {
			t.Errorf("parseGoModPins()[%q].PURL is empty", name)
		}
	}
}

func TestParseGoModPinsEmptyAndInvalid(t *testing.T) {
	got, err := parseGoModPins(" \n")
	if err != nil {
		t.Fatalf("parseGoModPins(empty) error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("parseGoModPins(empty) = %#v, want no pins", got)
	}

	got, err = parseGoModPins("module example.com/demo\n\ngo 1.21\n")
	if err != nil {
		t.Fatalf("parseGoModPins(no requires) error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("parseGoModPins(no requires) = %#v, want no pins", got)
	}
}

func TestCheckGoModOnlyChecksChangedRequires(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:golang/github.com/example/added": "v2.0.0"}}

	before := `module example.com/demo

require github.com/example/existing v1.0.0
`
	after := `module example.com/demo

require (
	github.com/example/existing v1.0.0
	github.com/example/added v1.0.0
)
`

	got, err := CheckGoMod(before, after, res)
	if err != nil {
		t.Fatalf("CheckGoMod() error = %v", err)
	}
	if res.lookups != 1 {
		t.Fatalf("CheckGoMod() made %d resolver lookups, want 1", res.lookups)
	}
	if len(got) != 1 {
		t.Fatalf("CheckGoMod() returned %d mismatches, want 1: %#v", len(got), got)
	}
	if got[0].Name != "github.com/example/added" || got[0].Current != "v1.0.0" || got[0].Latest != "v2.0.0" {
		t.Fatalf("CheckGoMod() mismatch = %#v", got[0])
	}
}

func TestCheckGoModAtLatestNoMismatch(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:golang/github.com/example/added": "v1.0.0"}}

	before := `module example.com/demo
`
	after := `module example.com/demo

require github.com/example/added v1.0.0
`

	got, err := CheckGoMod(before, after, res)
	if err != nil {
		t.Fatalf("CheckGoMod() error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("CheckGoMod() = %#v, want no mismatches", got)
	}
}

// TestCheckGoModPseudoVersionComparesOlderThanTaggedRelease covers the
// go.mod-specific gotcha noted in the package doc comment: a pseudo-version
// (an untagged commit pin) always compares as older than any real tagged
// release under the "golang" vers scheme.
func TestCheckGoModPseudoVersionComparesOlderThanTaggedRelease(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:golang/github.com/example/added": "v1.2.3"}}

	before := `module example.com/demo
`
	after := `module example.com/demo

require github.com/example/added v0.0.0-20210101000000-abcdef123456
`

	got, err := CheckGoMod(before, after, res)
	if err != nil {
		t.Fatalf("CheckGoMod() error = %v", err)
	}
	if len(got) != 1 {
		t.Fatalf("CheckGoMod() returned %d mismatches, want 1: %#v", len(got), got)
	}
	if got[0].Latest != "v1.2.3" {
		t.Fatalf("CheckGoMod() mismatch = %#v", got[0])
	}
}

// TestCheckGoModIncompatibleSuffixIgnoredInComparison covers the
// "+incompatible" build-metadata gotcha: it must not make an otherwise
// up-to-date pin look outdated (or vice versa).
func TestCheckGoModIncompatibleSuffixIgnoredInComparison(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:golang/github.com/example/added": "v2.3.4"}}

	before := `module example.com/demo
`
	after := `module example.com/demo

require github.com/example/added v2.3.4+incompatible
`

	got, err := CheckGoMod(before, after, res)
	if err != nil {
		t.Fatalf("CheckGoMod() error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("CheckGoMod() = %#v, want no mismatches (+incompatible is build metadata)", got)
	}
}

func TestCheckGoModUntouchedRequireIgnored(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:golang/github.com/example/other": "v9.0.0"}}

	before := `module example.com/demo

require github.com/example/other v1.0.0
`
	after := `module example.com/demo

require github.com/example/other v1.0.0

require github.com/example/added v1.0.0
`
	res.latest["pkg:golang/github.com/example/added"] = "v1.0.0"

	got, err := CheckGoMod(before, after, res)
	if err != nil {
		t.Fatalf("CheckGoMod() error = %v", err)
	}
	// "other" is outdated (v1.0.0 vs latest v9.0.0) but untouched by the
	// write, so only "added" should ever get looked up.
	if res.lookups != 1 {
		t.Fatalf("CheckGoMod() made %d resolver lookups, want 1", res.lookups)
	}
	if len(got) != 0 {
		t.Fatalf("CheckGoMod() = %#v, want no mismatches", got)
	}
}
