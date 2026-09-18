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
	for location, version := range want {
		if got[location].Version != version || got[location].Range {
			t.Errorf("parsePypiPins()[%q] = %#v, want exact %q", location, got[location], version)
		}
	}
	if pin := got["project/dependencies/flask"]; !pin.Range {
		t.Errorf("flask pin = %#v, want a range", pin)
	}
}

func TestParsePyprojectPinsPoetryCaretIsNotExact(t *testing.T) {
	// Poetry treats a bare version as a caret range, not an exact pin, so
	// it must be reported as a range, not an exact pin.
	content := `
[tool.poetry.dependencies]
requests = "2.32.4"
`
	got, err := parsePypiPins("pyproject.toml", content)
	if err != nil {
		t.Fatalf("parsePypiPins() error = %v", err)
	}
	if pin, ok := got["tool/poetry/dependencies/requests"]; !ok || !pin.Range {
		t.Fatalf("parsePypiPins() = %#v, want a range pin (not exact) for a bare Poetry version", got)
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

	got, err := CheckPyproject(before, after, res, true)
	if err != nil {
		t.Fatalf("CheckPyproject() error = %v", err)
	}
	if len(got) != 1 || got[0].Name != "httpx" || got[0].Current != "0.27.0" || got[0].Latest != httpxLatestVersion {
		t.Fatalf("CheckPyproject() = %#v, want one mismatch for httpx", got)
	}
}

func TestCheckPyprojectFlagsRangeWithNoLockfile(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:pypi/requests": requestsLatestVersion}}

	before := "[tool.poetry.dependencies]\n"
	after := "[tool.poetry.dependencies]\nrequests = \"^2.0.0\"\n"

	got, err := CheckPyproject(before, after, res, false)
	if err != nil {
		t.Fatalf("CheckPyproject() error = %v", err)
	}
	if len(got) != 1 || !got[0].Range || !got[0].NoLockfile {
		t.Fatalf("CheckPyproject() = %#v, want a lockfile-only mismatch since the caret range already allows latest", got)
	}
}

func TestCheckPyprojectFlagsPoetryCaretExcludingLatestWithCaretSuggestion(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:pypi/requests": requestsLatestVersion}}

	before := "[tool.poetry.dependencies]\n"
	after := "[tool.poetry.dependencies]\nrequests = \"^1.0.0\"\n"

	got, err := CheckPyproject(before, after, res, true)
	if err != nil {
		t.Fatalf("CheckPyproject() error = %v", err)
	}
	if len(got) != 1 || !got[0].Range || got[0].Suggested != "^"+requestsLatestVersion {
		t.Fatalf("CheckPyproject() = %#v, want a caret suggestion anchored at latest", got)
	}
}

func TestCheckPyprojectFlagsPEP621RangeExcludingLatestWithBoundedSuggestion(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:pypi/flask": "3.1.0"}}

	before := "[project]\nname = \"demo\"\ndependencies = []\n"
	after := "[project]\nname = \"demo\"\ndependencies = [\"flask<3.0.0\"]\n"

	got, err := CheckPyproject(before, after, res, true)
	if err != nil {
		t.Fatalf("CheckPyproject() error = %v", err)
	}
	if len(got) != 1 || !got[0].Range || got[0].Suggested != ">=3.1.0,<4.0.0" {
		t.Fatalf("CheckPyproject() = %#v, want a PEP 440 bounded-range suggestion", got)
	}
}
