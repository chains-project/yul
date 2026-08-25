package main

import (
	"context"
	"reflect"
	"testing"

	"github.com/chains-project/yul/pkg/githubactions"
	"github.com/chains-project/yul/pkg/golang"
	"github.com/chains-project/yul/pkg/ignore"
	"github.com/chains-project/yul/pkg/maven"
	"github.com/chains-project/yul/pkg/npm"
	"github.com/chains-project/yul/pkg/pypi"
	"github.com/chains-project/yul/pkg/util/mismatch"
)

type stubResolver struct{}

func (*stubResolver) LatestVersions(context.Context, []string) (map[string]string, error) {
	return nil, nil
}

func TestCheckerFor(t *testing.T) {
	tests := []struct {
		filename string
		want     any
	}{
		{filename: "pom.xml", want: maven.Checker{}},
		{filename: "requirements.txt", want: pypi.RequirementsChecker{}},
		{filename: "pyproject.toml", want: pypi.PyprojectChecker{}},
		{filename: "package.json", want: npm.Checker{}},
		{filename: ".github/workflows/ci.yml", want: githubactions.Checker{}},
		{filename: "/home/user/project/.github/workflows/release.yaml", want: githubactions.Checker{}},
		{filename: "go.mod", want: golang.Checker{}},
	}

	checkers := newCheckers(nil)
	for _, test := range tests {
		t.Run(test.filename, func(t *testing.T) {
			got := checkerFor(checkers, test.filename)
			if got == nil {
				t.Fatalf("checkerFor(%q) returned nil", test.filename)
			}
			if reflect.TypeOf(got) != reflect.TypeOf(test.want) {
				t.Fatalf("checkerFor(%q) returned %T, want %T", test.filename, got, test.want)
			}
		})
	}
}

func TestCheckerForUnknownManifest(t *testing.T) {
	if got := checkerFor(newCheckers(nil), "Gemfile"); got != nil {
		t.Fatalf("checkerFor(%q) returned %T, want nil", "Gemfile", got)
	}
}

func TestFilterIgnored(t *testing.T) {
	mismatches := []mismatch.Mismatch{
		{Name: "lodash", Current: "4.17.20", Latest: "4.17.21", PURL: "pkg:npm/lodash"},
		{Name: "requests", Current: "2.30.0", Latest: "2.32.0", PURL: "pkg:pypi/requests"},
	}
	ignored := ignore.Set{"pkg:npm/lodash@4.17.20": true}

	got := filterIgnored(mismatches, ignored)
	if len(got) != 1 || got[0].Name != "requests" {
		t.Fatalf("filterIgnored() = %+v, want only the requests mismatch", got)
	}
}

func TestFilterIgnoredKeepsMismatchWhenVersionDiffers(t *testing.T) {
	mismatches := []mismatch.Mismatch{
		{Name: "lodash", Current: "4.17.19", Latest: "4.17.21", PURL: "pkg:npm/lodash"},
	}
	// The ignore entry covers a different pinned version than what's
	// actually being written, so it shouldn't suppress this mismatch.
	ignored := ignore.Set{"pkg:npm/lodash@4.17.20": true}

	got := filterIgnored(mismatches, ignored)
	if len(got) != 1 {
		t.Fatalf("filterIgnored() = %+v, want the mismatch kept", got)
	}
}

func TestFilterIgnoredNoIgnores(t *testing.T) {
	mismatches := []mismatch.Mismatch{
		{Name: "lodash", Current: "4.17.20", Latest: "4.17.21", PURL: "pkg:npm/lodash"},
	}
	got := filterIgnored(mismatches, ignore.Set{})
	if len(got) != 1 {
		t.Fatalf("filterIgnored() = %+v, want the mismatch kept", got)
	}
}

func TestNewCheckersWiresResolverIntoMaven(t *testing.T) {
	res := &stubResolver{}
	checker, ok := checkerFor(newCheckers(res), "pom.xml").(maven.Checker)
	if !ok {
		t.Fatal("pom.xml checker is not maven.Checker")
	}
	if checker.Resolver != res {
		t.Fatal("maven.Checker does not use the shared resolver")
	}
}
