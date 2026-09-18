package pins

import (
	"context"
	"testing"

	"github.com/chains-project/yul/pkg/util/mismatch"
)

func TestExactVersion(t *testing.T) {
	tests := []struct {
		name            string
		spec            string
		scheme          string
		requireOperator bool
		want            string
		wantOK          bool
	}{
		{name: "npm bare version is exact", spec: "1.2.3", scheme: "npm", want: "1.2.3", wantOK: true},
		{name: "npm prerelease is exact", spec: "2.0.0-rc.1", scheme: "npm", want: "2.0.0-rc.1", wantOK: true},
		{name: "npm build metadata is exact", spec: "3.0.0+metadata", scheme: "npm", want: "3.0.0+metadata", wantOK: true},
		{name: "npm caret range is not exact", spec: "^4.0.0", scheme: "npm"},
		{name: "npm tilde range is not exact", spec: "~4.0.0", scheme: "npm"},
		{name: "npm dist-tag is not exact", spec: "latest", scheme: "npm"},
		{name: "npm workspace protocol is not exact", spec: "workspace:*", scheme: "npm"},

		{name: "pypi == is exact", spec: "==2.32.4", scheme: "pypi", requireOperator: true, want: "2.32.4", wantOK: true},
		{name: "pypi marker is stripped", spec: "== 0.28.1 ; python_version >= \"3.10\"", scheme: "pypi", requireOperator: true, want: "0.28.1", wantOK: true},
		{name: "pypi >= is not exact", spec: ">=3.0.0", scheme: "pypi", requireOperator: true},
		{name: "pypi ~= is not exact", spec: "~=1.4.2", scheme: "pypi", requireOperator: true},
		{name: "pypi != is not exact", spec: "!=2.0.0", scheme: "pypi", requireOperator: true},
		{name: "pypi bounded range is not exact", spec: ">=1.0.0,<2.0.0", scheme: "pypi", requireOperator: true},
		{name: "pypi redundant exact bound collapses to exact", spec: "==2.0.0,<3.0.0", scheme: "pypi", requireOperator: true, want: "2.0.0", wantOK: true},
		{name: "pypi unrelated exclusion remains exact", spec: "==2.0.0,!=3.0.0", scheme: "pypi", requireOperator: true, want: "2.0.0", wantOK: true},
		{name: "pypi bare version is not exact when operator required", spec: "1.2.3", scheme: "pypi", requireOperator: true},
		{name: "pypi caret is not exact", spec: "^1.2.3", scheme: "pypi", requireOperator: true},
		{name: "pypi empty spec is not exact", spec: "", scheme: "pypi", requireOperator: true},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			got, ok := ExactVersion(test.spec, test.scheme, test.requireOperator)
			if ok != test.wantOK || got != test.want {
				t.Fatalf("ExactVersion(%q, %q, %v) = (%q, %v), want (%q, %v)",
					test.spec, test.scheme, test.requireOperator, got, ok, test.want, test.wantOK)
			}
		})
	}
}

func TestIsRange(t *testing.T) {
	tests := []struct {
		name            string
		spec            string
		scheme          string
		requireOperator bool
		want            bool
	}{
		{name: "npm caret is a range", spec: "^4.0.0", scheme: "npm", want: true},
		{name: "npm tilde is a range", spec: "~4.0.0", scheme: "npm", want: true},
		{name: "npm x-range is a range", spec: "1.2.x", scheme: "npm", want: true},
		{name: "npm wildcard is a range", spec: "*", scheme: "npm", want: true},
		{name: "npm exact version is not a range", spec: "1.2.3", scheme: "npm"},
		{name: "npm dist-tag is not a range", spec: "latest", scheme: "npm"},
		{name: "npm workspace protocol is not a range", spec: "workspace:*", scheme: "npm"},

		{name: "pypi bounded range is a range", spec: ">=1.0.0,<2.0.0", scheme: "pypi", requireOperator: true, want: true},
		{name: "pypi tilde-equal is a range", spec: "~=1.4.2", scheme: "pypi", requireOperator: true, want: true},
		{name: "poetry caret is a range", spec: "^2.32.4", scheme: "pypi", requireOperator: true, want: true},
		{name: "poetry tilde is a range", spec: "~2.32.4", scheme: "pypi", requireOperator: true, want: true},
		{name: "poetry bare version is a range", spec: "2.32.4", scheme: "pypi", requireOperator: true, want: true},
		{name: "pypi exact pin is not a range", spec: "==2.32.4", scheme: "pypi", requireOperator: true},
		{name: "pypi redundant exact bound is not a range", spec: "==2.0.0,<3.0.0", scheme: "pypi", requireOperator: true},
		{name: "pypi empty spec is not a range", spec: "", scheme: "pypi", requireOperator: true},

		{name: "cargo caret is a range", spec: "^1.2.3", scheme: "cargo", requireOperator: true, want: true},
		{name: "cargo bare version is a range", spec: "1.2.3", scheme: "cargo", requireOperator: true, want: true},
		{name: "cargo exact pin is not a range", spec: "=1.2.3", scheme: "cargo", requireOperator: true},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			if got := IsRange(test.spec, test.scheme, test.requireOperator); got != test.want {
				t.Fatalf("IsRange(%q, %q, %v) = %v, want %v", test.spec, test.scheme, test.requireOperator, got, test.want)
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
		"unchanged": {Name: "unchanged", Spec: "1.0.0", PURL: "pkg:npm/unchanged"},
		"changed":   {Name: "changed", Spec: "1.0.0", PURL: "pkg:npm/changed"},
	}
	after := map[string]Pin{
		"unchanged": {Name: "unchanged", Spec: "1.0.0", PURL: "pkg:npm/unchanged"},
		"changed":   {Name: "changed", Spec: "2.0.0", PURL: "pkg:npm/changed"},
		"added":     {Name: "added", Spec: "1.0.0", PURL: "pkg:npm/added"},
	}

	got, err := Diff(context.Background(), before, after, "npm", res, true, nil)
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
		"current": {Name: "current", Spec: "1.0.0", PURL: "pkg:npm/current"},
		"newer":   {Name: "newer", Spec: "2.0.0", PURL: "pkg:npm/newer"},
	}

	got, err := Diff(context.Background(), before, after, "npm", res, true, nil)
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
		"dependencies/package": {Name: "original", Spec: "1.0.0", PURL: "pkg:npm/original"},
	}
	after := map[string]Pin{
		"dependencies/package": {Name: "replacement", Spec: "1.0.0", PURL: "pkg:npm/replacement"},
	}

	got, err := Diff(context.Background(), before, after, "npm", res, true, nil)
	if err != nil {
		t.Fatalf("Diff() error = %v", err)
	}
	if len(got) != 1 || got[0].Name != "replacement" || got[0].Latest != "2.0.0" {
		t.Fatalf("Diff() = %#v, want replacement mismatch", got)
	}
}

func TestDiffFailsOpenOnUnresolvedPurl(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{}}

	before := map[string]Pin{}
	after := map[string]Pin{
		"unknown": {Name: "unknown", Spec: "1.0.0", PURL: "pkg:npm/unknown"},
	}

	if _, err := Diff(context.Background(), before, after, "npm", res, true, nil); err == nil {
		t.Fatal("Diff() returned nil error, want an error for an unresolved purl")
	}
}

func TestDiffRanges(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{
		"pkg:npm/added":   "2.0.0",
		"pkg:npm/changed": "3.0.0",
		"pkg:npm/current": "1.0.0",
	}}
	format := func(_, v string) string { return "^" + v }

	before := map[string]Pin{
		"unchanged": {Name: "unchanged", Spec: "^1.0.0", PURL: "pkg:npm/current", Range: true},
		"changed":   {Name: "changed", Spec: "^1.0.0", PURL: "pkg:npm/changed", Range: true},
	}
	after := map[string]Pin{
		"unchanged": {Name: "unchanged", Spec: "^1.0.0", PURL: "pkg:npm/current", Range: true},
		"changed":   {Name: "changed", Spec: "^2.0.0", PURL: "pkg:npm/changed", Range: true},
		"added":     {Name: "added", Spec: "^1.0.0", PURL: "pkg:npm/added", Range: true},
	}

	got, err := Diff(context.Background(), before, after, "npm", res, true, format)
	if err != nil {
		t.Fatalf("Diff() error = %v", err)
	}
	if len(got) != 2 {
		t.Fatalf("Diff() returned %d mismatches, want 2: %#v", len(got), got)
	}

	byName := make(map[string]mismatch.Mismatch)
	for _, m := range got {
		byName[m.Name] = m
	}
	if m := byName["added"]; !m.Range || m.Latest != "2.0.0" || m.Suggested != "^2.0.0" || m.NoLockfile {
		t.Fatalf("Diff() added mismatch = %#v", m)
	}
	if m := byName["changed"]; !m.Range || m.Latest != "3.0.0" || m.Suggested != "^3.0.0" || m.NoLockfile {
		t.Fatalf("Diff() changed mismatch = %#v", m)
	}
}

func TestDiffRangesSkipsUntouchedRanges(t *testing.T) {
	// latest "2.0.0" falls outside "^1.0.0" (>=1.0.0,<2.0.0), so a newly
	// added range at that location is expected to be flagged.
	res := &fakeResolver{latest: map[string]string{"pkg:npm/current": "2.0.0"}}
	format := func(_, v string) string { return v }

	before := map[string]Pin{}
	after := map[string]Pin{
		"current": {Name: "current", Spec: "^1.0.0", PURL: "pkg:npm/current", Range: true},
	}

	got, err := Diff(context.Background(), before, before, "npm", res, true, format)
	if err != nil {
		t.Fatalf("Diff() error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("Diff() = %#v, want no mismatches when before == after", got)
	}

	got, err = Diff(context.Background(), before, after, "npm", res, true, format)
	if err != nil {
		t.Fatalf("Diff() error = %v", err)
	}
	if len(got) != 1 {
		t.Fatalf("Diff() = %#v, want one mismatch for a newly added range", got)
	}
}

func TestDiffRangesSkipsRangeThatAlreadyAllowsLatestWithLockfile(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:npm/current": "1.5.0"}}
	format := func(_, v string) string { return v }

	before := map[string]Pin{}
	after := map[string]Pin{
		"current": {Name: "current", Spec: "^1.0.0", PURL: "pkg:npm/current", Range: true},
	}

	got, err := Diff(context.Background(), before, after, "npm", res, true, format)
	if err != nil {
		t.Fatalf("Diff() error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("Diff() = %#v, want no mismatches when the range already allows latest and a lockfile is present", got)
	}
}

func TestDiffRangesFlagsRangeThatAllowsLatestButHasNoLockfile(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:npm/current": "1.5.0"}}
	format := func(_, v string) string { return v }

	before := map[string]Pin{}
	after := map[string]Pin{
		"current": {Name: "current", Spec: "^1.0.0", PURL: "pkg:npm/current", Range: true},
	}

	got, err := Diff(context.Background(), before, after, "npm", res, false, format)
	if err != nil {
		t.Fatalf("Diff() error = %v", err)
	}
	if len(got) != 1 || !got[0].Range || got[0].Suggested != "" || !got[0].NoLockfile {
		t.Fatalf("Diff() = %#v, want a lockfile-only mismatch with no Suggested fix", got)
	}
}

func TestDiffRangesFailsOpenOnUnresolvedPurl(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{}}
	format := func(_, v string) string { return v }

	before := map[string]Pin{}
	after := map[string]Pin{
		"unknown": {Name: "unknown", Spec: "^1.0.0", PURL: "pkg:npm/unknown", Range: true},
	}

	if _, err := Diff(context.Background(), before, after, "npm", res, true, format); err == nil {
		t.Fatal("Diff() returned nil error, want an error for an unresolved purl")
	}
}
