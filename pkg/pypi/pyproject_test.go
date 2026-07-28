package pypi

import "testing"

func TestParsePyproject(t *testing.T) {
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

	got, err := parsePyproject(content)
	if err != nil {
		t.Fatalf("parsePyproject() error = %v", err)
	}
	want := map[string]string{
		requestsPackage: latestRequestsVersion,
		"pytest":        "8.3.5",
	}
	if len(got) != len(want) {
		t.Fatalf("parsePyproject() returned %d pins, want %d: %#v", len(got), len(want), got)
	}
	for name, version := range want {
		if got[name] != version {
			t.Errorf("parsePyproject()[%q] = %q, want %q", name, got[name], version)
		}
	}
}

func TestParsePyprojectEmptyAndInvalid(t *testing.T) {
	got, err := parsePyproject(" \n")
	if err != nil {
		t.Fatalf("parsePyproject(empty) error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("parsePyproject(empty) = %#v, want no pins", got)
	}

	if _, err := parsePyproject("[project"); err == nil {
		t.Fatal("parsePyproject(invalid) returned nil error")
	}
}
