package pypi

import "testing"

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
	want := map[string]string{
		"requests": "2.32.4",
		"pytest":   "8.3.5",
	}
	if len(got) != len(want) {
		t.Fatalf("parsePypiPins() returned %d pins, want %d: %#v", len(got), len(want), got)
	}
	for name, version := range want {
		if got[name].Version != version {
			t.Errorf("parsePypiPins()[%q].Version = %q, want %q", name, got[name].Version, version)
		}
	}
}

func TestParsePyprojectPinsPoetryCaretIsNotExact(t *testing.T) {
	// Poetry treats a bare version as a caret range, not an exact pin, so
	// it must not be reported even though it looks like a plain version.
	content := `
[tool.poetry.dependencies]
requests = "2.32.4"
`
	got, err := parsePypiPins("pyproject.toml", content)
	if err != nil {
		t.Fatalf("parsePypiPins() error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("parsePypiPins() = %#v, want no exact pins for a bare Poetry version", got)
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
	res := &fakeResolver{latest: map[string]string{"pkg:pypi/httpx": "0.28.1"}}

	before := "[project]\nname = \"demo\"\ndependencies = [\"click==8.1.3\"]\n"
	after := "[project]\nname = \"demo\"\ndependencies = [\"click==8.1.3\", \"httpx==0.27.0\"]\n"

	got, err := CheckPyproject(before, after, res)
	if err != nil {
		t.Fatalf("CheckPyproject() error = %v", err)
	}
	if len(got) != 1 || got[0].Name != "httpx" || got[0].Current != "0.27.0" || got[0].Latest != "0.28.1" {
		t.Fatalf("CheckPyproject() = %#v, want one mismatch for httpx", got)
	}
}
