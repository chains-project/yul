package pypi

import (
	"testing"

	"github.com/chains-project/yul/pkg/util/pins"
)

func TestParsePyprojectPins(t *testing.T) {
	content := `
[project]
name = "example"
dependencies = [
    "Requests==2.32.4",
    "flask>=3.0.0",
]

[project.optional-dependencies]
test = [
    "pytest==8.3.5",
]
docs = [
    "sphinx~=8.0",
]
`

	got, err := parsePypiPins("pyproject.toml", content)
	if err != nil {
		t.Fatalf("parsePypiPins() error = %v", err)
	}
	want := map[string]pins.Spec{
		"project/dependencies/requests":             {Operator: "==", Version: requestsLatestVersion},
		"project/dependencies/flask":                {Operator: ">=", Version: "3.0.0"},
		"project/optional-dependencies/test/pytest": {Operator: "==", Version: "8.3.5"},
		"project/optional-dependencies/docs/sphinx": {Operator: "~=", Version: "8.0"},
	}
	if len(got) != len(want) {
		t.Fatalf("parsePypiPins() returned %d pins, want %d: %#v", len(got), len(want), got)
	}
	for location, spec := range want {
		if got[location].Operator != spec.Operator || got[location].Version != spec.Version {
			t.Errorf("parsePypiPins()[%q] = %q %q, want %q %q", location, got[location].Operator, got[location].Version, spec.Operator, spec.Version)
		}
	}
}

func TestParsePyprojectPinsPoetryRanges(t *testing.T) {
	// Poetry treats a bare version as a caret range. It's still a
	// requirement with one base version, so it's kept current in place,
	// with the (absent) operator preserved.
	content := `
[tool.poetry.dependencies]
bare = "2.32.4"
caret = "^1.2"
tilde = "~1.2.3"
wildcard = "*"
table = { version = "^3.0", optional = true }
`
	got, err := parsePypiPins("pyproject.toml", content)
	if err != nil {
		t.Fatalf("parsePypiPins() error = %v", err)
	}
	want := map[string]pins.Spec{
		"tool/poetry/dependencies/bare":  {Version: "2.32.4"},
		"tool/poetry/dependencies/caret": {Operator: "^", Version: "1.2"},
		"tool/poetry/dependencies/tilde": {Operator: "~", Version: "1.2.3"},
		"tool/poetry/dependencies/table": {Operator: "^", Version: "3.0"},
	}
	if len(got) != len(want) {
		t.Fatalf("parsePypiPins() returned %d pins, want %d: %#v", len(got), len(want), got)
	}
	for location, spec := range want {
		if got[location].Operator != spec.Operator || got[location].Version != spec.Version {
			t.Errorf("parsePypiPins()[%q] = %q %q, want %q %q", location, got[location].Operator, got[location].Version, spec.Operator, spec.Version)
		}
	}
}

func TestCheckPyprojectRangeIsBumpedInPlace(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{
		"pkg:pypi/flask":  "3.1.0",
		"pkg:pypi/poetry": "2.5.1",
	}}

	before := ""
	after := "[project]\nname = \"demo\"\ndependencies = [\"flask>=3.0.0\"]\n\n[tool.poetry.dependencies]\npoetry = \"^2.0\"\n"

	got, err := CheckPyproject(before, after, res)
	if err != nil {
		t.Fatalf("CheckPyproject() error = %v", err)
	}
	want := map[string][2]string{
		"flask":  {">=3.0.0", ">=3.1.0"},
		"poetry": {"^2.0", "^2.5.1"},
	}
	if len(got) != len(want) {
		t.Fatalf("CheckPyproject() returned %d mismatches, want %d: %#v", len(got), len(want), got)
	}
	for _, m := range got {
		w, ok := want[m.Name]
		if !ok || m.Current != w[0] || m.Latest != w[1] {
			t.Errorf("CheckPyproject() mismatch for %s = %q -> %q, want %q -> %q", m.Name, m.Current, m.Latest, w[0], w[1])
		}
	}
}

func TestParsePyprojectPinsEmptyAndInvalid(t *testing.T) {
	got, err := parsePypiPins("pyproject.toml", " \n")
	if err != nil {
		t.Fatalf("parsePypiPins(empty) error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("parsePypiPins(empty) = %#v, want no pins", got)
	}

	if _, err := parsePypiPins("pyproject.toml", "[project"); err == nil {
		t.Fatal("parsePypiPins(invalid) returned nil error")
	}
}

func TestCheckPyprojectOnlyChecksChangedPins(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:pypi/httpx": httpxLatestVersion}}

	before := "[project]\nname = \"demo\"\ndependencies = [\"click==8.1.3\"]\n"
	after := "[project]\nname = \"demo\"\ndependencies = [\"click==8.1.3\", \"httpx==0.27.0\"]\n"

	got, err := CheckPyproject(before, after, res)
	if err != nil {
		t.Fatalf("CheckPyproject() error = %v", err)
	}
	if len(got) != 1 || got[0].Name != "httpx" || got[0].Current != "==0.27.0" || got[0].Latest != "=="+httpxLatestVersion {
		t.Fatalf("CheckPyproject() = %#v, want one mismatch for httpx", got)
	}
}
