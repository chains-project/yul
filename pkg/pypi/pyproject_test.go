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
		"project/dependencies/requests":             requestsLatestVersion,
		"project/optional-dependencies/test/pytest": "8.3.5",
	}
	if len(got) != len(want) {
		t.Fatalf("parsePypiPins() returned %d pins, want %d: %#v", len(got), len(want), got)
	}
	for location, version := range want {
		if got[location].Version != version {
			t.Errorf("parsePypiPins()[%q].Version = %q, want %q", location, got[location].Version, version)
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
	res := &fakeResolver{latest: map[string]string{"pkg:pypi/httpx": httpxLatestVersion}}

	before := "[project]\nname = \"demo\"\ndependencies = [\"click==8.1.3\"]\n"
	after := "[project]\nname = \"demo\"\ndependencies = [\"click==8.1.3\", \"httpx==0.27.0\"]\n"

	got, err := CheckPyproject(before, after, res)
	if err != nil {
		t.Fatalf("CheckPyproject() error = %v", err)
	}
	if len(got) != 1 || got[0].Name != "httpx" || got[0].Current != "0.27.0" || got[0].Latest != httpxLatestVersion {
		t.Fatalf("CheckPyproject() = %#v, want one mismatch for httpx", got)
	}
}

func TestParsePyprojectRangesCoversPoetryCaretAndPEP621Bounds(t *testing.T) {
	content := `
[project]
name = "demo"
dependencies = [
    "flask>=3.0.0",
]

[tool.poetry.dependencies]
requests = "^2.32.4"
`
	got, err := parsePypiRanges("pyproject.toml", content)
	if err != nil {
		t.Fatalf("parsePypiRanges() error = %v", err)
	}
	want := map[string]string{
		"project/dependencies/flask":        ">=3.0.0",
		"tool/poetry/dependencies/requests": "^2.32.4",
	}
	if len(got) != len(want) {
		t.Fatalf("parsePypiRanges() returned %d ranges, want %d: %#v", len(got), len(want), got)
	}
	for location, spec := range want {
		if got[location].Spec != spec {
			t.Errorf("parsePypiRanges()[%q].Spec = %q, want %q", location, got[location].Spec, spec)
		}
	}
}

func TestCheckPyprojectFlagsPoetryCaretAsRange(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:pypi/requests": requestsLatestVersion}}

	before := "[tool.poetry.dependencies]\n"
	after := "[tool.poetry.dependencies]\nrequests = \"^1.0.0\"\n"

	got, err := CheckPyproject(before, after, res)
	if err != nil {
		t.Fatalf("CheckPyproject() error = %v", err)
	}
	if len(got) != 1 || !got[0].Range || got[0].Current != "^1.0.0" || got[0].Suggested != "=="+requestsLatestVersion {
		t.Fatalf("CheckPyproject() = %#v, want one range recommendation for requests", got)
	}
}

func TestCheckPyprojectSkipsPoetryCaretThatAlreadyAllowsLatest(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:pypi/requests": requestsLatestVersion}}

	before := "[tool.poetry.dependencies]\n"
	after := "[tool.poetry.dependencies]\nrequests = \"^2.0.0\"\n"

	got, err := CheckPyproject(before, after, res)
	if err != nil {
		t.Fatalf("CheckPyproject() error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("CheckPyproject() = %#v, want no mismatches when the caret range already allows latest", got)
	}
}
