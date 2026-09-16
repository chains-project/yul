package pypi

import (
	"testing"

	"github.com/chains-project/yul/pkg/util/pins"
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

	got, err := parsePypiPins("requirements.txt", content)
	if err != nil {
		t.Fatalf("parsePypiPins() error = %v", err)
	}
	want := map[string]pins.Spec{
		"requirements/requests": {Operator: "==", Version: requestsLatestVersion},
		"requirements/flask":    {Operator: ">=", Version: "3.0.0"},
		"requirements/httpx":    {Operator: "==", Version: httpxLatestVersion},
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

func TestParseRequirementsPinsRejectsSpecifiersWithoutABaseVersion(t *testing.T) {
	content := `
exclusion!=2.0.0
upper<3.0.0
strict>2.0.0
ranged>=2.0.0,<3.0.0
wildcard==2.0.*
unpinned
`
	got, err := parsePypiPins("requirements.txt", content)
	if err != nil {
		t.Fatalf("parsePypiPins() error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("parsePypiPins() = %#v, want no pins", got)
	}
}

func TestCheckRequirementsOnlyChecksChangedPins(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{
		"pkg:pypi/requests": requestsLatestVersion,
		"pkg:pypi/flask":    "3.0.0",
	}}

	before := "existing==1.0.0\n"
	after := "existing==1.0.0\nrequests==2.31.0\nflask>=3.0.0\nranged>=1.0,<2.0\n"

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
	if got[0].Name != "requests" || got[0].Current != "==2.31.0" || got[0].Latest != "=="+requestsLatestVersion {
		t.Fatalf("CheckRequirements() mismatch = %#v", got[0])
	}
}

func TestCheckRequirementsRangeIsBumpedInPlace(t *testing.T) {
	res := &fakeResolver{latest: map[string]string{
		"pkg:pypi/minimum":    "3.1.0",
		"pkg:pypi/compatible": "2.4.0",
	}}

	got, err := CheckRequirements("", "minimum>=3.0.0\ncompatible~=2.0\n", res)
	if err != nil {
		t.Fatalf("CheckRequirements() error = %v", err)
	}
	want := map[string][2]string{
		"minimum":    {">=3.0.0", ">=3.1.0"},
		"compatible": {"~=2.0", "~=2.4.0"},
	}
	if len(got) != len(want) {
		t.Fatalf("CheckRequirements() returned %d mismatches, want %d: %#v", len(got), len(want), got)
	}
	for _, m := range got {
		w, ok := want[m.Name]
		if !ok || m.Current != w[0] || m.Latest != w[1] {
			t.Errorf("CheckRequirements() mismatch for %s = %q -> %q, want %q -> %q", m.Name, m.Current, m.Latest, w[0], w[1])
		}
	}
}
