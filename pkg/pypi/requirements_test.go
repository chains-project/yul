package pypi

import (
	"testing"

	"github.com/chains-project/yul/pkg/util/mismatch"
)

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

	got, err := parsePypi("requirements.txt", content)
	if err != nil {
		t.Fatalf("parsePypi() error = %v", err)
	}
	want := map[string]string{
		"requirements/requests": requestsLatestVersion,
		"requirements/httpx":    httpxLatestVersion,
	}
	for location, version := range want {
		if got[location].Spec != version || got[location].Range {
			t.Errorf("parsePypi()[%q] = %#v, want exact %q", location, got[location], version)
		}
	}
}

func TestParseRequirementsPinsUsesCanonicalPURL(t *testing.T) {
	got, err := parsePypi("requirements.txt", "Django_Rest.Framework==1.0\n")
	if err != nil {
		t.Fatalf("parsePypi() error = %v", err)
	}
	pin := got["requirements/django-rest-framework"]
	if pin.Name != "django-rest.framework" || pin.PURL != "pkg:pypi/django-rest.framework" {
		t.Fatalf("canonical pin = %#v", pin)
	}
}

func TestParseRequirementsPinsEmptyAndInvalid(t *testing.T) {
	got, err := parsePypi("requirements.txt", " \n")
	if err != nil {
		t.Fatalf("parsePypi(empty) error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("parsePypi(empty) = %#v, want no pins", got)
	}
}

func TestParseRequirementsPinsRejectsLooseSpecifiers(t *testing.T) {
	content := `
minimum>=2.0.0
compatible~=2.0.0
exclusion!=2.0.0
ranged>=2.0.0,<3.0.0
`
	got, err := parsePypi("requirements.txt", content)
	if err != nil {
		t.Fatalf("parsePypi() error = %v", err)
	}
	for location, pin := range got {
		if !pin.Range {
			t.Errorf("parsePypi()[%q] = %#v, want a range not an exact pin", location, pin)
		}
	}
}

func TestCheckRequirementsOnlyChecksChangedPinsAndRanges(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{
		"pkg:pypi/requests": requestsLatestVersion,
		"pkg:pypi/flask":    "3.1.0",
	}}

	before := "existing==1.0.0\n"
	after := "existing==1.0.0\nrequests==2.31.0\nflask<3.0.0\n"

	got, err := CheckRequirements(before, after, res)
	if err != nil {
		t.Fatalf("CheckRequirements() error = %v", err)
	}
	if len(got) != 2 {
		t.Fatalf("CheckRequirements() returned %d mismatches, want 2: %#v", len(got), got)
	}

	byName := make(map[string]mismatch.Mismatch, len(got))
	for _, m := range got {
		byName[m.Name] = m
	}
	if m := byName["requests"]; m.Current != "2.31.0" || m.Latest != requestsLatestVersion || m.Range {
		t.Fatalf("CheckRequirements() requests mismatch = %#v", m)
	}
	if m := byName["flask"]; m.Current != "<3.0.0" || m.Latest != "3.1.0" || m.Suggested != ">=3.1.0,<4.0.0" || !m.Range {
		t.Fatalf("CheckRequirements() flask mismatch = %#v", m)
	}
}

// TestCheckRequirementsNeverFlagsMissingLockfile checks requirements.txt
// never reports a NoLockfile mismatch, since it has no lockfile convention
// of its own to check for - even when the hook is told none is present.
func TestCheckRequirementsNeverFlagsMissingLockfile(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{"pkg:pypi/flask": "3.1.0"}}

	before := ""
	after := "flask>=3.0.0\n"

	got, err := CheckRequirements(before, after, res)
	if err != nil {
		t.Fatalf("CheckRequirements() error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("CheckRequirements() = %#v, want no mismatches: the range allows latest and requirements.txt has no lockfile to check for", got)
	}
}
