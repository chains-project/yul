package pypi

import "testing"

const (
	requestsLatestVersion = "2.32.4"
	httpxLatestVersion    = "0.28.1"
)

func TestParseRequirementsPins(t *testing.T) {
	content := `
# application dependencies
Requests==2.32.4
flask>=3.0.0
-r development.txt
httpx[http2] == 0.28.1 ; python_version >= "3.10"
`

	got, err := parsePypiPins("requirements.txt", content)
	if err != nil {
		t.Fatalf("parsePypiPins() error = %v", err)
	}
	want := map[string]string{
		"requirements/requests": requestsLatestVersion,
		"requirements/httpx":    httpxLatestVersion,
	}
	for location, version := range want {
		if got[location].Version != version || got[location].Range {
			t.Errorf("parsePypiPins()[%q] = %#v, want exact %q", location, got[location], version)
		}
	}
	if pin := got["requirements/flask"]; !pin.Range {
		t.Errorf("flask pin = %#v, want a range", pin)
	}
}

func TestParseRequirementsPinsUsesCanonicalPURL(t *testing.T) {
	got, err := parsePypiPins("requirements.txt", "Django_Rest.Framework==1.0\n")
	if err != nil {
		t.Fatalf("parsePypiPins() error = %v", err)
	}
	pin := got["requirements/django-rest-framework"]
	if pin.Name != "django-rest.framework" || pin.PURL != "pkg:pypi/django-rest.framework" {
		t.Fatalf("canonical pin = %#v", pin)
	}
}

func TestParseRequirementsPinsEmptyAndInvalid(t *testing.T) {
	got, err := parsePypiPins("requirements.txt", " \n")
	if err != nil {
		t.Fatalf("parsePypiPins(empty) error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("parsePypiPins(empty) = %#v, want no pins", got)
	}
}

func TestParseRequirementsPinsRejectsLooseSpecifiers(t *testing.T) {
	// These aren't exact pins, but they are ranges - not ignored outright.
	content := `
minimum>=2.0.0
compatible~=2.0.0
exclusion!=2.0.0
ranged>=2.0.0,<3.0.0
`
	got, err := parsePypiPins("requirements.txt", content)
	if err != nil {
		t.Fatalf("parsePypiPins() error = %v", err)
	}
	for location, pin := range got {
		if !pin.Range {
			t.Errorf("parsePypiPins()[%q] = %#v, want a range not an exact pin", location, pin)
		}
	}
}

func TestCheckRequirementsOnlyChecksChangedPins(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{
		"pkg:pypi/requests": requestsLatestVersion,
		"pkg:pypi/flask":    "3.5.0", // satisfies ">=3.0.0"; never flagged (no lockfile check here)
	}}

	before := "existing==1.0.0\n"
	after := "existing==1.0.0\nrequests==2.31.0\nflask>=3.0.0\n"

	got, err := CheckRequirements(before, after, res)
	if err != nil {
		t.Fatalf("CheckRequirements() error = %v", err)
	}
	if len(got) != 1 {
		t.Fatalf("CheckRequirements() returned %d mismatches, want 1: %#v", len(got), got)
	}
	if got[0].Name != "requests" || got[0].Current != "2.31.0" || got[0].Latest != requestsLatestVersion {
		t.Fatalf("CheckRequirements() mismatch = %#v", got[0])
	}
}

func TestCheckRequirementsNeverFlagsMissingLockfile(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:pypi/flask": "3.1.0"}}

	got, err := CheckRequirements("", "flask>=3.0.0\n", res)
	if err != nil {
		t.Fatalf("CheckRequirements() error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("CheckRequirements() = %#v, want no mismatches: the range allows latest and requirements.txt has no lockfile to check for", got)
	}
}
