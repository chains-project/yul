package pypi

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

func TestParseRequirements(t *testing.T) {
	content := `
# application dependencies
Requests==2.32.4
flask>=3.0.0
-r development.txt
httpx[http2] == 0.28.1 ; python_version >= "3.10"
`

	got := parseRequirements(content)
	want := map[string]string{
		requestsPackage: latestRequestsVersion,
		"httpx":         "0.28.1",
	}
	if len(got) != len(want) {
		t.Fatalf("parseRequirements() returned %d pins, want %d: %#v", len(got), len(want), got)
	}
	for name, version := range want {
		if got[name] != version {
			t.Errorf("parseRequirements()[%q] = %q, want %q", name, got[name], version)
		}
	}
}

func TestCheckRequirementsOnlyChecksChangedPins(t *testing.T) {
	originalTransport := http.DefaultTransport
	requests := 0
	http.DefaultTransport = roundTripFunc(func(req *http.Request) (*http.Response, error) {
		requests++
		if req.URL.String() != "https://pypi.org/pypi/requests/json" {
			t.Fatalf("unexpected registry request: %s", req.URL)
		}
		return &http.Response{
			StatusCode: http.StatusOK,
			Status:     "200 OK",
			Body:       io.NopCloser(strings.NewReader(`{"info":{"version":"2.32.4"}}`)),
			Header:     make(http.Header),
		}, nil
	})
	t.Cleanup(func() {
		http.DefaultTransport = originalTransport
	})

	before := "existing==1.0.0\n"
	after := "existing==1.0.0\nrequests==2.31.0\nflask>=3.0.0\n"

	got, err := CheckRequirements(before, after)
	if err != nil {
		t.Fatalf("CheckRequirements() error = %v", err)
	}
	if requests != 1 {
		t.Fatalf("CheckRequirements() made %d registry requests, want 1", requests)
	}
	if len(got) != 1 {
		t.Fatalf("CheckRequirements() returned %d mismatches, want 1: %#v", len(got), got)
	}
	if got[0].Name != requestsPackage || got[0].Current != "2.31.0" || got[0].Latest != latestRequestsVersion {
		t.Fatalf("CheckRequirements() mismatch = %#v", got[0])
	}
}
