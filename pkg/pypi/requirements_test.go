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
	if len(got) != len(want) {
		t.Fatalf("parsePypiPins() returned %d pins, want %d: %#v", len(got), len(want), got)
	}
	for location, version := range want {
		if got[location].Version != version {
			t.Errorf("parsePypiPins()[%q].Version = %q, want %q", location, got[location].Version, version)
		}
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
	if len(got) != 0 {
		t.Fatalf("parsePypiPins() = %#v, want no exact pins", got)
	}
}

func TestCheckRequirementsOnlyChecksChangedPins(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:pypi/requests": requestsLatestVersion}}

	before := "existing==1.0.0\n"
	after := "existing==1.0.0\nrequests==2.31.0\nflask>=3.0.0\n"

	got, err := CheckRequirements(before, after, res)
	if err != nil {
		t.Fatalf("CheckRequirements() error = %v", err)
	}
	if res.lookups != 1 {
		t.Fatalf("CheckRequirements() made %d resolver lookups, want 1", res.lookups)
	}
	if len(got) != 1 {
		t.Fatalf("CheckRequirements() returned %d mismatches, want 1: %#v", len(got), got)
	}
	if got[0].Name != "requests" || got[0].Current != "2.31.0" || got[0].Latest != requestsLatestVersion {
		t.Fatalf("CheckRequirements() mismatch = %#v", got[0])
	}
}
