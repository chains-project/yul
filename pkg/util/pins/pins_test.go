package pins

import (
	"context"
	"testing"
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
	res := &fakeResolver{latest: map[string]string{"pkg:npm/current": "1.0.0"}}

	before := map[string]Pin{}
	after := map[string]Pin{
		"current": {Name: "current", Version: "1.0.0", PURL: "pkg:npm/current"},
	}

	got, err := Diff(context.Background(), before, after, "npm", res)
	if err != nil {
		t.Fatalf("Diff() error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("Diff() = %#v, want no mismatches for an up-to-date pin", got)
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
