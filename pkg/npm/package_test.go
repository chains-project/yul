package npm

import (
	"io"
	"net/http"
	"strings"
	"testing"
)

type roundTripFunc func(*http.Request) (*http.Response, error)

func (f roundTripFunc) RoundTrip(req *http.Request) (*http.Response, error) {
	return f(req)
}

func TestParsePackageJSON(t *testing.T) {
	content := `{
		"dependencies": {
			"runtime": "1.2.3",
			"prerelease": "2.0.0-rc.1",
			"build": "3.0.0+metadata",
			"range": "^4.0.0",
			"tag": "latest",
			"workspace": "workspace:*"
		},
		"devDependencies": {
			"development": "5.0.0"
		},
		"optionalDependencies": {
			"optional": "6.0.0"
		},
		"peerDependencies": {
			"peer": "7.0.0"
		}
	}`

	got, err := parsePackageJSON(content)
	if err != nil {
		t.Fatalf("parsePackageJSON() error = %v", err)
	}

	want := map[string]string{
		"runtime":     "1.2.3",
		"prerelease":  "2.0.0-rc.1",
		"build":       "3.0.0+metadata",
		"development": "5.0.0",
		"optional":    "6.0.0",
		"peer":        "7.0.0",
	}
	if len(got) != len(want) {
		t.Fatalf("parsePackageJSON() returned %d pins, want %d: %#v", len(got), len(want), got)
	}
	for name, version := range want {
		if got[name] != version {
			t.Errorf("parsePackageJSON()[%q] = %q, want %q", name, got[name], version)
		}
	}
}

func TestParsePackageJSONEmptyAndInvalid(t *testing.T) {
	got, err := parsePackageJSON(" \n")
	if err != nil {
		t.Fatalf("parsePackageJSON(empty) error = %v", err)
	}
	if len(got) != 0 {
		t.Fatalf("parsePackageJSON(empty) = %#v, want no pins", got)
	}

	if _, err := parsePackageJSON("{"); err == nil {
		t.Fatal("parsePackageJSON(invalid) returned nil error")
	}
}

func TestCheckPackageJSONOnlyChecksChangedExactPins(t *testing.T) {
	originalTransport := http.DefaultTransport
	requests := 0
	http.DefaultTransport = roundTripFunc(func(req *http.Request) (*http.Response, error) {
		requests++
		if req.URL.String() != "https://registry.npmjs.org/added" {
			t.Fatalf("unexpected registry request: %s", req.URL)
		}
		return &http.Response{
			StatusCode: http.StatusOK,
			Status:     "200 OK",
			Body:       io.NopCloser(strings.NewReader(`{"dist-tags":{"latest":"2.0.0"}}`)),
			Header:     make(http.Header),
		}, nil
	})
	t.Cleanup(func() {
		http.DefaultTransport = originalTransport
	})

	before := `{"dependencies":{"existing":"1.0.0"}}`
	after := `{"dependencies":{"existing":"1.0.0","added":"1.0.0","range":"^1.0.0"}}`

	got, err := CheckPackageJSON(before, after)
	if err != nil {
		t.Fatalf("CheckPackageJSON() error = %v", err)
	}
	if requests != 1 {
		t.Fatalf("CheckPackageJSON() made %d registry requests, want 1", requests)
	}
	if len(got) != 1 {
		t.Fatalf("CheckPackageJSON() returned %d mismatches, want 1: %#v", len(got), got)
	}
	if got[0].Name != "added" || got[0].Current != "1.0.0" || got[0].Latest != "2.0.0" {
		t.Fatalf("CheckPackageJSON() mismatch = %#v", got[0])
	}
}
