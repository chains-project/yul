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

	got, err := parsePypi("pyproject.toml", content)
	if err != nil {
		t.Fatalf("parsePypi() error = %v", err)
	}
	want := map[string]string{
		"project/dependencies/requests":             requestsLatestVersion,
		"project/optional-dependencies/test/pytest": "8.3.5",
	}
	for location, version := range want {
		if got[location].Spec != version || got[location].Range {
			t.Errorf("parsePypi()[%q] = %#v, want exact %q", location, got[location], version)
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
	got, err := parsePypi("pyproject.toml", content)
	if err != nil {
		t.Fatalf("parsePypi() error = %v", err)
	}
	if pin, ok := got["tool/poetry/dependencies/requests"]; !ok || !pin.Range {
		t.Fatalf("parsePypi() = %#v, want a range pin (not exact) for a bare Poetry version", got)
	}
}

func TestParsePyprojectPinsEmptyAndInvalid(t *testing.T) {
	got, err := parsePypi("pyproject.toml", " \n")
	if err != nil {
		t.Fatalf("parsePypi(empty) error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("parsePypi(empty) = %#v, want no pins", got)
	}

	if _, err := parsePypi("pyproject.toml", "[project"); err == nil {
		t.Fatal("parsePypi(invalid) returned nil error")
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
	got, err := parsePypi("pyproject.toml", content)
	if err != nil {
		t.Fatalf("parsePypi() error = %v", err)
	}
	want := map[string]string{
		"project/dependencies/flask":        ">=3.0.0",
		"tool/poetry/dependencies/requests": "^2.32.4",
	}
	for location, spec := range want {
		if got[location].Spec != spec || !got[location].Range {
			t.Errorf("parsePypi()[%q] = %#v, want range %q", location, got[location], spec)
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
