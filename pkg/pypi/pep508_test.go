package pypi

import "testing"

func TestNormalizePackageName(t *testing.T) {
	tests := map[string]string{
		"Requests":          "requests",
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
