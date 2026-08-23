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
	// Cargo.toml stands in for an unsupported manifest now that go.mod (the
	// previous stand-in) has its own checker.
	if got := checkerFor(newCheckers(nil), "Cargo.toml"); got != nil {
		t.Fatalf("checkerFor(%q) returned %T, want nil", "Cargo.toml", got)
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
