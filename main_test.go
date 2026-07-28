package main

import (
	"reflect"
	"testing"

	"github.com/chains-project/yul/pkg/maven"
	"github.com/chains-project/yul/pkg/npm"
	"github.com/chains-project/yul/pkg/pypi"
)

func TestCheckerFor(t *testing.T) {
	tests := []struct {
		filename string
		want     any
	}{
		{filename: "pom.xml", want: maven.Checker{}},
		{filename: "requirements.txt", want: pypi.RequirementsChecker{}},
		{filename: "pyproject.toml", want: pypi.PyprojectChecker{}},
		{filename: "package.json", want: npm.Checker{}},
	}

	for _, test := range tests {
		t.Run(test.filename, func(t *testing.T) {
			got := checkerFor(test.filename)
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
	if got := checkerFor("go.mod"); got != nil {
		t.Fatalf("checkerFor(%q) returned %T, want nil", "go.mod", got)
	}
}
