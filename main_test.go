package main

import (
	"context"
	"reflect"
	"testing"

	"github.com/chains-project/yul/pkg/githubactions"
	"github.com/chains-project/yul/pkg/golang"
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

func TestNewCheckersWiresExistenceIntoMaven(t *testing.T) {
	withResolver := checkerFor(newCheckers(&stubResolver{}), "pom.xml").(maven.Checker)
	if withResolver.Existence == nil {
		t.Error("newCheckers(res) left maven.Checker.Existence nil")
	}

	matchOnly := checkerFor(newCheckers(nil), "pom.xml").(maven.Checker)
	if matchOnly.Existence != nil {
		t.Error("newCheckers(nil) set maven.Checker.Existence; the match-only pass needs no network client")
	}
}

func TestMismatchDetail(t *testing.T) {
	tests := []struct {
		name string
		m    mismatch.Mismatch
		want string
	}{
		{
			name: "outdated",
			m:    mismatch.Mismatch{Current: "1.0.0", Latest: "2.0.0"},
			want: "1.0.0 -> 2.0.0",
		},
		{
			name: "outdated with suggested sha",
			m:    mismatch.Mismatch{Current: "v4", Latest: "v4.2.0", Suggested: "abc123"},
			want: "v4 -> abc123",
		},
		{
			name: "missing package",
			m:    mismatch.Mismatch{Current: "1.0.0", Kind: mismatch.KindMissingPackage},
			want: "does not exist - hallucinated package, remove it or use a real coordinate",
		},
		{
			name: "missing version",
			m:    mismatch.Mismatch{Current: "9.9.9", Kind: mismatch.KindMissingVersion},
			want: "version 9.9.9 was never published - hallucinated version",
		},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			if got := mismatchDetail(test.m); got != test.want {
				t.Fatalf("mismatchDetail() = %q, want %q", got, test.want)
			}
		})
	}
}

func TestAnyHallucinated(t *testing.T) {
	outdatedOnly := []mismatch.Mismatch{{Kind: mismatch.KindOutdated}, {Kind: mismatch.KindOutdated}}
	if anyHallucinated(outdatedOnly) {
		t.Error("anyHallucinated(outdated only) = true")
	}
	mixed := []mismatch.Mismatch{{Kind: mismatch.KindOutdated}, {Kind: mismatch.KindMissingPackage}}
	if !anyHallucinated(mixed) {
		t.Error("anyHallucinated(with missing package) = false")
	}
}
