package pins

import (
	"context"
	"testing"
)

func TestParseSpec(t *testing.T) {
	tests := []struct {
		name        string
		spec        string
		scheme      string
		bareIsRange bool
		want        Spec
		wantOK      bool
	}{
		{name: "npm bare version is exact", spec: "1.2.3", scheme: "npm", want: Spec{Version: "1.2.3"}, wantOK: true},
		{name: "npm prerelease is exact", spec: "2.0.0-rc.1", scheme: "npm", want: Spec{Version: "2.0.0-rc.1"}, wantOK: true},
		{name: "npm build metadata is exact", spec: "3.0.0+metadata", scheme: "npm", want: Spec{Version: "3.0.0+metadata"}, wantOK: true},
		{name: "npm caret range keeps operator", spec: "^4.0.0", scheme: "npm", want: Spec{Operator: "^", Version: "4.0.0"}, wantOK: true},
		{name: "npm tilde range keeps operator", spec: "~4.0.0", scheme: "npm", want: Spec{Operator: "~", Version: "4.0.0"}, wantOK: true},
		{name: "npm >= range keeps operator", spec: ">=4.0.0", scheme: "npm", want: Spec{Operator: ">=", Version: "4.0.0"}, wantOK: true},
		{name: "npm operator with space", spec: ">= 4.0.0", scheme: "npm", want: Spec{Operator: ">=", Version: "4.0.0"}, wantOK: true},
		{name: "npm bare partial version is an x-range, not exact", spec: "1.2", scheme: "npm"},
		{name: "npm x-range is not supported", spec: "1.x", scheme: "npm"},
		{name: "npm hyphen range is not supported", spec: "1.0.0 - 2.0.0", scheme: "npm"},
		{name: "npm bounded range is not supported", spec: ">=1.0.0 <2.0.0", scheme: "npm"},
		{name: "npm or range is not supported", spec: "^1.0.0 || ^2.0.0", scheme: "npm"},
		{name: "npm strict lower bound is not supported", spec: ">1.0.0", scheme: "npm"},
		{name: "npm upper bound is not supported", spec: "<2.0.0", scheme: "npm"},
		{name: "npm wildcard is not supported", spec: "*", scheme: "npm"},
		{name: "npm dist-tag is not supported", spec: "latest", scheme: "npm"},
		{name: "npm workspace protocol is not supported", spec: "workspace:*", scheme: "npm"},

		{name: "pypi == is exact", spec: "==2.32.4", scheme: "pypi", bareIsRange: true, want: Spec{Operator: "==", Version: "2.32.4"}, wantOK: true},
		{name: "pypi marker is stripped", spec: "== 0.28.1 ; python_version >= \"3.10\"", scheme: "pypi", bareIsRange: true, want: Spec{Operator: "==", Version: "0.28.1"}, wantOK: true},
		{name: "pypi >= keeps operator", spec: ">=3.0.0", scheme: "pypi", bareIsRange: true, want: Spec{Operator: ">=", Version: "3.0.0"}, wantOK: true},
		{name: "pypi ~= keeps operator", spec: "~=1.4.2", scheme: "pypi", bareIsRange: true, want: Spec{Operator: "~=", Version: "1.4.2"}, wantOK: true},
		{name: "pypi poetry caret keeps operator", spec: "^1.2.3", scheme: "pypi", bareIsRange: true, want: Spec{Operator: "^", Version: "1.2.3"}, wantOK: true},
		{name: "pypi poetry tilde keeps operator", spec: "~1.2", scheme: "pypi", bareIsRange: true, want: Spec{Operator: "~", Version: "1.2"}, wantOK: true},
		{name: "pypi poetry bare version is a caret range", spec: "1.2.3", scheme: "pypi", bareIsRange: true, want: Spec{Version: "1.2.3"}, wantOK: true},
		{name: "pypi != is not supported", spec: "!=2.0.0", scheme: "pypi", bareIsRange: true},
		{name: "pypi < is not supported", spec: "<2.0.0", scheme: "pypi", bareIsRange: true},
		{name: "pypi > is not supported", spec: ">2.0.0", scheme: "pypi", bareIsRange: true},
		{name: "pypi === is not supported", spec: "===2.0.0", scheme: "pypi", bareIsRange: true},
		{name: "pypi bounded range is not supported", spec: ">=1.0.0,<2.0.0", scheme: "pypi", bareIsRange: true},
		{name: "pypi exact with extra bound is not supported", spec: "==2.0.0,<3.0.0", scheme: "pypi", bareIsRange: true},
		{name: "pypi wildcard pin is not supported", spec: "==1.2.*", scheme: "pypi", bareIsRange: true},
		{name: "pypi empty spec is not supported", spec: "", scheme: "pypi", bareIsRange: true},

		{name: "cargo bare version is a caret range", spec: "1.0.107", scheme: "cargo", bareIsRange: true, want: Spec{Version: "1.0.107"}, wantOK: true},
		{name: "cargo bare partial version is a caret range", spec: "1.2", scheme: "cargo", bareIsRange: true, want: Spec{Version: "1.2"}, wantOK: true},
		{name: "cargo = is exact", spec: "=1.2.3", scheme: "cargo", bareIsRange: true, want: Spec{Operator: "=", Version: "1.2.3"}, wantOK: true},
		{name: "cargo caret keeps operator", spec: "^1.2.3", scheme: "cargo", bareIsRange: true, want: Spec{Operator: "^", Version: "1.2.3"}, wantOK: true},
		{name: "cargo tilde keeps operator", spec: "~1.2.3", scheme: "cargo", bareIsRange: true, want: Spec{Operator: "~", Version: "1.2.3"}, wantOK: true},
		{name: "cargo wildcard is not supported", spec: "*", scheme: "cargo", bareIsRange: true},
		{name: "cargo partial wildcard is not supported", spec: "1.*", scheme: "cargo", bareIsRange: true},
		{name: "cargo multi-clause range is not supported", spec: ">=1.2, <1.5", scheme: "cargo", bareIsRange: true},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			got, ok := ParseSpec(test.spec, test.scheme, test.bareIsRange)
			if ok != test.wantOK || got != test.want {
				t.Fatalf("ParseSpec(%q, %q, %v) = (%#v, %v), want (%#v, %v)",
					test.spec, test.scheme, test.bareIsRange, got, ok, test.want, test.wantOK)
			}
		})
	}
}

func TestExactVersion(t *testing.T) {
	tests := []struct {
		name   string
		spec   string
		scheme string
		want   string
		wantOK bool
	}{
		{name: "golang version is exact", spec: "v1.2.3", scheme: "golang", want: "v1.2.3", wantOK: true},
		{name: "maven hard requirement is exact", spec: "[1.2.3]", scheme: "maven", want: "1.2.3", wantOK: true},
		{name: "maven range is not exact", spec: "[1.0,2.0)", scheme: "maven"},
		{name: "npm caret range is not exact", spec: "^4.0.0", scheme: "npm"},
		{name: "empty spec is not exact", spec: "", scheme: "npm"},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			got, ok := ExactVersion(test.spec, test.scheme)
			if ok != test.wantOK || got != test.want {
				t.Fatalf("ExactVersion(%q, %q) = (%q, %v), want (%q, %v)",
					test.spec, test.scheme, got, ok, test.want, test.wantOK)
			}
		})
	}
}

type fakeResolver struct {
	latest map[string]string
}

func (r *fakeResolver) LatestVersions(ctx context.Context, purls []string) (map[string]string, error) {
	result := make(map[string]string, len(purls))
	for _, purl := range purls {
		if v, ok := r.latest[purl]; ok {
			result[purl] = v
		}
	}
	return result, nil
}

func TestDiff(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{
		"pkg:npm/added":   "2.0.0",
		"pkg:npm/changed": "3.0.0",
	}}

	before := map[string]Pin{
		"unchanged": {Name: "unchanged", Version: "1.0.0", PURL: "pkg:npm/unchanged"},
		"changed":   {Name: "changed", Version: "1.0.0", PURL: "pkg:npm/changed"},
	}
	after := map[string]Pin{
		"unchanged": {Name: "unchanged", Version: "1.0.0", PURL: "pkg:npm/unchanged"},
		"changed":   {Name: "changed", Version: "2.0.0", PURL: "pkg:npm/changed"},
		"added":     {Name: "added", Version: "1.0.0", PURL: "pkg:npm/added"},
	}

	got, err := Diff(context.Background(), before, after, "npm", res)
	if err != nil {
		t.Fatalf("Diff() error = %v", err)
	}
	if len(got) != 2 {
		t.Fatalf("Diff() returned %d mismatches, want 2: %#v", len(got), got)
	}

	byName := make(map[string]string)
	for _, m := range got {
		byName[m.Name] = m.Latest
	}
	if byName["added"] != "2.0.0" || byName["changed"] != "3.0.0" {
		t.Fatalf("Diff() = %#v", got)
	}
}

func TestDiffSkipsUntouchedAndUpToDatePins(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{
		"pkg:npm/current": "1.0.0",
		"pkg:npm/newer":   "1.0.0",
	}}

	before := map[string]Pin{}
	after := map[string]Pin{
		"current": {Name: "current", Version: "1.0.0", PURL: "pkg:npm/current"},
		"newer":   {Name: "newer", Version: "2.0.0", PURL: "pkg:npm/newer"},
	}

	got, err := Diff(context.Background(), before, after, "npm", res)
	if err != nil {
		t.Fatalf("Diff() error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("Diff() = %#v, want no mismatches for current or newer pins", got)
	}
}

func TestDiffChecksReplacementAtSameLocation(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{
		"pkg:npm/replacement": "2.0.0",
	}}

	before := map[string]Pin{
		"dependencies/package": {Name: "original", Version: "1.0.0", PURL: "pkg:npm/original"},
	}
	after := map[string]Pin{
		"dependencies/package": {Name: "replacement", Version: "1.0.0", PURL: "pkg:npm/replacement"},
	}

	got, err := Diff(context.Background(), before, after, "npm", res)
	if err != nil {
		t.Fatalf("Diff() error = %v", err)
	}
	if len(got) != 1 || got[0].Name != "replacement" || got[0].Latest != "2.0.0" {
		t.Fatalf("Diff() = %#v, want replacement mismatch", got)
	}
}

func TestDiffKeepsOperatorInSuggestion(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{
		"pkg:npm/caret":   "0.5.1",
		"pkg:npm/minimum": "2.0.0",
		"pkg:npm/current": "1.0.0",
	}}

	before := map[string]Pin{}
	after := map[string]Pin{
		"caret":   {Name: "caret", Operator: "^", Version: "0.1.0", PURL: "pkg:npm/caret"},
		"minimum": {Name: "minimum", Operator: ">=", Version: "1.0.0", PURL: "pkg:npm/minimum"},
		"current": {Name: "current", Operator: "^", Version: "1.0.0", PURL: "pkg:npm/current"},
	}

	got, err := Diff(context.Background(), before, after, "npm", res)
	if err != nil {
		t.Fatalf("Diff() error = %v", err)
	}
	if len(got) != 2 {
		t.Fatalf("Diff() returned %d mismatches, want 2: %#v", len(got), got)
	}
	want := map[string][2]string{
		"caret":   {"^0.1.0", "^0.5.1"},
		"minimum": {">=1.0.0", ">=2.0.0"},
	}
	for _, m := range got {
		w, ok := want[m.Name]
		if !ok || m.Current != w[0] || m.Latest != w[1] {
			t.Errorf("Diff() mismatch for %s = %q -> %q, want %q -> %q", m.Name, m.Current, m.Latest, w[0], w[1])
		}
	}
}

// TestDiffRangeCrossesMajorBoundary: a caret range never admits a new
// major (^0.1.0 excludes 1.0.0), but yul compares the base version alone,
// so the suggestion is ^1.0.0. The manifest should name the latest
// release even when the range itself would never have resolved to it.
func TestDiffRangeCrossesMajorBoundary(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{
		"pkg:npm/caret": "1.0.0",
		"pkg:npm/tilde": "2.3.0",
	}}

	after := map[string]Pin{
		"caret": {Name: "caret", Operator: "^", Version: "0.1.0", PURL: "pkg:npm/caret"},
		"tilde": {Name: "tilde", Operator: "~", Version: "1.4.2", PURL: "pkg:npm/tilde"},
	}

	got, err := Diff(context.Background(), map[string]Pin{}, after, "npm", res)
	if err != nil {
		t.Fatalf("Diff() error = %v", err)
	}
	want := map[string][2]string{
		"caret": {"^0.1.0", "^1.0.0"},
		"tilde": {"~1.4.2", "~2.3.0"},
	}
	if len(got) != len(want) {
		t.Fatalf("Diff() returned %d mismatches, want %d: %#v", len(got), len(want), got)
	}
	for _, m := range got {
		w := want[m.Name]
		if m.Current != w[0] || m.Latest != w[1] {
			t.Errorf("Diff() mismatch for %s = %q -> %q, want %q -> %q", m.Name, m.Current, m.Latest, w[0], w[1])
		}
	}
}

func TestDiffChangedOperatorCountsAsChange(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:npm/dep": "2.0.0"}}

	before := map[string]Pin{
		"dep": {Name: "dep", Operator: "", Version: "1.0.0", PURL: "pkg:npm/dep"},
	}
	after := map[string]Pin{
		"dep": {Name: "dep", Operator: "^", Version: "1.0.0", PURL: "pkg:npm/dep"},
	}

	got, err := Diff(context.Background(), before, after, "npm", res)
	if err != nil {
		t.Fatalf("Diff() error = %v", err)
	}
	if len(got) != 1 || got[0].Current != "^1.0.0" || got[0].Latest != "^2.0.0" {
		t.Fatalf("Diff() = %#v, want one mismatch ^1.0.0 -> ^2.0.0", got)
	}
}

func TestDiffFailsOpenOnUnresolvedPurl(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{}}

	before := map[string]Pin{}
	after := map[string]Pin{
		"unknown": {Name: "unknown", Version: "1.0.0", PURL: "pkg:npm/unknown"},
	}

	if _, err := Diff(context.Background(), before, after, "npm", res); err == nil {
		t.Fatal("Diff() returned nil error, want an error for an unresolved purl")
	}
}
