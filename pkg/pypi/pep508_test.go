package pypi

import "testing"

const (
	requestsPackage       = "requests"
	latestRequestsVersion = "2.32.4"
)

func TestParseRequirementLine(t *testing.T) {
	tests := []struct {
		name        string
		line        string
		wantName    string
		wantVersion string
		wantOK      bool
	}{
		{
			name:        "exact pin",
			line:        "requests==2.32.4",
			wantName:    requestsPackage,
			wantVersion: latestRequestsVersion,
			wantOK:      true,
		},
		{
			name:        "extras marker and comment",
			line:        `My_Package.Name[security] == 1.2.3 ; python_version >= "3.10" # supported versions`,
			wantName:    "my-package-name",
			wantVersion: "1.2.3",
			wantOK:      true,
		},
		{name: "blank", line: "  "},
		{name: "comment", line: "# requests==2.32.4"},
		{name: "include", line: "-r base.txt"},
		{name: "minimum", line: "requests>=2.0.0"},
		{name: "compatible", line: "requests~=2.0.0"},
		{name: "exclusion", line: "requests!=2.0.0"},
		{name: "multiple specifiers", line: "requests==2.0.0,<3.0.0"},
		{name: "missing name", line: "==2.0.0"},
		{name: "missing version", line: "requests=="},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			gotName, gotVersion, gotOK := parseRequirementLine(test.line)
			if gotName != test.wantName || gotVersion != test.wantVersion || gotOK != test.wantOK {
				t.Fatalf(
					"parseRequirementLine(%q) = (%q, %q, %t), want (%q, %q, %t)",
					test.line,
					gotName,
					gotVersion,
					gotOK,
					test.wantName,
					test.wantVersion,
					test.wantOK,
				)
			}
		})
	}
}

func TestNormalizePackageName(t *testing.T) {
	tests := map[string]string{
		"Requests":          requestsPackage,
		"My_Package.Name":   "my-package-name",
		"many---separators": "many-separators",
		"-surrounded-":      "surrounded",
	}

	for input, want := range tests {
		if got := normalizePackageName(input); got != want {
			t.Errorf("normalizePackageName(%q) = %q, want %q", input, got, want)
		}
	}
}
