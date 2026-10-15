package resolver

import (
	"context"
	"io"
	"net/http"
	"slices"
	"strings"
	"testing"

	"github.com/git-pkgs/vers"
)

type fallbackStub struct {
	got []string
}

func (f *fallbackStub) LatestVersions(_ context.Context, purls []string) (map[string]string, error) {
	f.got = append(f.got, purls...)
	latest := make(map[string]string, len(purls))
	for _, p := range purls {
		latest[p] = "v1.0.0"
	}
	return latest, nil
}

// TestRegistryResolverLatestVersions queries the real registries. Latest
// versions move, so each package is only checked for a stable version at
// least as new as one already released. Each was picked because its
// registry also lists something a naive lookup would get wrong: a beta
// dist-tag (npm), a post-release (PyPI), a 1.0.0 alpha (Cargo), an
// uppercase module path (Go), and milestones (Maven).
func TestRegistryResolverLatestVersions(t *testing.T) {
	tests := []struct {
		purl, scheme, atLeast string
	}{
		{"pkg:npm/%40vitejs/plugin-react", "npm", "4.0.0"},
		{"pkg:pypi/python-dateutil", "pypi", "2.9.0.post0"},
		{"pkg:cargo/libc", "cargo", "0.2.150"},
		{"pkg:golang/github.com/BurntSushi/toml", "golang", "v1.3.0"},
		{"pkg:maven/org.springframework.boot/spring-boot-starter-web", "maven", "3.0.0"},
	}

	fallback := &fallbackStub{}
	r := &RegistryResolver{Fallback: fallback}

	purls := []string{
		"pkg:npm/yul-test-package-that-does-not-exist",
		"pkg:githubactions/actions/checkout",
	}
	for _, test := range tests {
		purls = append(purls, test.purl)
	}
	got, err := r.LatestVersions(context.Background(), purls)
	if err != nil {
		t.Fatalf("LatestVersions() error = %v", err)
	}

	for _, test := range tests {
		v, ok := got[test.purl]
		if !ok {
			t.Errorf("%s: no latest version", test.purl)
			continue
		}
		if !vers.IsStableWithScheme(v, test.scheme) {
			t.Errorf("%s: latest %q is not a stable version", test.purl, v)
		}
		if vers.CompareWithScheme(v, test.atLeast, test.scheme) < 0 {
			t.Errorf("%s: latest %q is older than %q", test.purl, v, test.atLeast)
		}
	}

	slices.Sort(fallback.got)
	if want := []string{"pkg:githubactions/actions/checkout", "pkg:npm/yul-test-package-that-does-not-exist"}; !slices.Equal(fallback.got, want) {
		t.Errorf("fallback got %v, want %v", fallback.got, want)
	}
}

// statusTransport answers every request with the status its URL's path
// maps to, or 200 with body if the path isn't listed.
type statusTransport struct {
	status map[string]int
	body   string
}

func (s statusTransport) RoundTrip(req *http.Request) (*http.Response, error) {
	code, ok := s.status[req.URL.Path]
	if !ok {
		code = http.StatusOK
	}
	return &http.Response{StatusCode: code, Body: io.NopCloser(strings.NewReader(s.body)), Request: req}, nil
}

// knownFallback resolves only the purls in latest, like ecosyste.ms
// knowing some packages the registry doesn't.
type knownFallback map[string]string

func (f knownFallback) LatestVersions(_ context.Context, purls []string) (map[string]string, error) {
	latest := make(map[string]string)
	for _, p := range purls {
		if v, ok := f[p]; ok {
			latest[p] = v
		}
	}
	return latest, nil
}

// TestRegistryResolverReportsNotFound checks that only a registry's own
// "doesn't exist" answer, unconfirmed by the fallback, is reported as
// NotFound, and not a lookup that just failed.
func TestRegistryResolverReportsNotFound(t *testing.T) {
	r := &RegistryResolver{
		Fallback: knownFallback{"pkg:pypi/known-to-fallback": "1.0.0"},
		Client: &http.Client{Transport: statusTransport{
			body: `{"info": {"version": "2.0.0"}}`,
			status: map[string]int{
				"/pypi/hallucinated/json":           http.StatusNotFound,
				"/pypi/known-to-fallback/json":      http.StatusNotFound,
				"/pypi/server-error/json":           http.StatusInternalServerError,
				"/example.com/hallucinated/@latest": http.StatusGone,
			},
		}},
	}

	got, err := r.LatestVersions(context.Background(), []string{
		"pkg:pypi/hallucinated",
		"pkg:pypi/known-to-fallback",
		"pkg:pypi/server-error",
		"pkg:golang/example.com/hallucinated",
		"pkg:pypi/exists",
	})
	if err != nil {
		t.Fatalf("LatestVersions() error = %v", err)
	}

	want := map[string]string{
		"pkg:pypi/hallucinated":               NotFound,
		"pkg:pypi/known-to-fallback":          "1.0.0",
		"pkg:golang/example.com/hallucinated": NotFound,
		"pkg:pypi/exists":                     "2.0.0",
	}
	for p, v := range want {
		if gotV, ok := got[p]; !ok || gotV != v {
			t.Errorf("%s: got %q (present %v), want %q", p, gotV, ok, v)
		}
	}
	if _, ok := got["pkg:pypi/server-error"]; ok {
		t.Errorf("pkg:pypi/server-error: got %q, want it left out", got["pkg:pypi/server-error"])
	}
}
