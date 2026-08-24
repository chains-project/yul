package cocoapods

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

func TestParsePodfilePins(t *testing.T) {
	content := `
platform :ios, '13.0'

target 'App' do
  pod 'Exact', '5.6.4'
  pod 'Pessimistic', '~> 5.0'
  pod 'NoVersion'
  pod 'RangeOp', '>= 1.0'

  target 'AppTests' do
    inherit! :search_paths
    pod 'Exact', '1.0.0'
  end
end
`

	got, err := parsePodfilePins(content)
	if err != nil {
		t.Fatalf("parsePodfilePins() error = %v", err)
	}

	want := map[string]string{
		"runtime/Exact": "5.6.4",
		"test/Exact":    "1.0.0",
	}
	if len(got) != len(want) {
		t.Fatalf("parsePodfilePins() returned %d pins, want %d: %#v", len(got), len(want), got)
	}
	for location, version := range want {
		pin, ok := got[location]
		if !ok {
			t.Errorf("parsePodfilePins() missing %q", location)
			continue
		}
		if pin.Version != version {
			t.Errorf("parsePodfilePins()[%q].Version = %q, want %q", location, pin.Version, version)
		}
		if pin.PURL == "" {
			t.Errorf("parsePodfilePins()[%q].PURL is empty", location)
		}
	}
}

func TestParsePodfilePinsEmptyAndInvalid(t *testing.T) {
	got, err := parsePodfilePins(" \n")
	if err != nil {
		t.Fatalf("parsePodfilePins(empty) error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("parsePodfilePins(empty) = %#v, want no pins", got)
	}

	got, err = parsePodfilePins("platform :ios, '13.0'\n")
	if err != nil {
		t.Fatalf("parsePodfilePins(no pods) error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("parsePodfilePins(no pods) = %#v, want no pins", got)
	}
}

func TestCheckPodfileOnlyChecksChangedPods(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:cocoapods/Added": "2.0.0"}}

	before := `target 'App' do
  pod 'Existing', '1.0.0'
end
`
	after := `target 'App' do
  pod 'Existing', '1.0.0'
  pod 'Added', '1.0.0'
end
`

	got, err := CheckPodfile(before, after, res)
	if err != nil {
		t.Fatalf("CheckPodfile() error = %v", err)
	}
	if res.lookups != 1 {
		t.Fatalf("CheckPodfile() made %d resolver lookups, want 1", res.lookups)
	}
	if len(got) != 1 {
		t.Fatalf("CheckPodfile() returned %d mismatches, want 1: %#v", len(got), got)
	}
	if got[0].Name != "Added" || got[0].Current != "1.0.0" || got[0].Latest != "2.0.0" {
		t.Fatalf("CheckPodfile() mismatch = %#v", got[0])
	}
}

func TestCheckPodfileAtLatestNoMismatch(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:cocoapods/Added": "1.0.0"}}

	before := `target 'App' do
end
`
	after := `target 'App' do
  pod 'Added', '1.0.0'
end
`

	got, err := CheckPodfile(before, after, res)
	if err != nil {
		t.Fatalf("CheckPodfile() error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("CheckPodfile() = %#v, want no mismatches", got)
	}
}

// TestCheckPodfilePessimisticOperatorNotExact covers the CocoaPods-specific
// gotcha noted in the package doc comment: a `~>` pessimistic-operator pin
// is a range, not an exact pin, and must never be flagged even when its
// floor is older than the latest release.
func TestCheckPodfilePessimisticOperatorNotExact(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:cocoapods/Added": "9.0.0"}}

	before := `target 'App' do
end
`
	after := `target 'App' do
  pod 'Added', '~> 1.0'
end
`

	got, err := CheckPodfile(before, after, res)
	if err != nil {
		t.Fatalf("CheckPodfile() error = %v", err)
	}
	if res.lookups != 0 {
		t.Fatalf("CheckPodfile() made %d resolver lookups, want 0 (pessimistic operator isn't an exact pin)", res.lookups)
	}
	if len(got) != 0 {
		t.Fatalf("CheckPodfile() = %#v, want no mismatches for a `~>` pin", got)
	}
}

func TestCheckPodfileUntouchedPodIgnored(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:cocoapods/Other": "9.0.0"}}

	before := `target 'App' do
  pod 'Other', '1.0.0'
end
`
	after := `target 'App' do
  pod 'Other', '1.0.0'
  pod 'Added', '1.0.0'
end
`
	res.latest["pkg:cocoapods/Added"] = "1.0.0"

	got, err := CheckPodfile(before, after, res)
	if err != nil {
		t.Fatalf("CheckPodfile() error = %v", err)
	}
	// "Other" is outdated (1.0.0 vs latest 9.0.0) but untouched by the
	// write, so only "Added" should ever get looked up.
	if res.lookups != 1 {
		t.Fatalf("CheckPodfile() made %d resolver lookups, want 1", res.lookups)
	}
	if len(got) != 0 {
		t.Fatalf("CheckPodfile() = %#v, want no mismatches", got)
	}
}
