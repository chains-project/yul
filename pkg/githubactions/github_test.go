package githubactions

import (
	"context"
	"maps"
	"net/http"
	"net/http/httptest"
	"slices"
	"testing"
)

type fallbackStub struct {
	got []string
}

func (f *fallbackStub) LatestVersions(_ context.Context, purls []string) (map[string]string, error) {
	f.got = append(f.got, purls...)
	latest := make(map[string]string, len(purls))
	for _, p := range purls {
		latest[p] = "v0.0.1"
	}
	return latest, nil
}

type shaStub struct{}

func (shaStub) ResolveSHA(context.Context, string, string) (string, error) {
	return "fallbacksha", nil
}

func newGitHubServer(t *testing.T) *httptest.Server {
	t.Helper()
	return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Header.Get("Authorization") != "Bearer tok" {
			http.Error(w, "unauthorized", http.StatusUnauthorized)
			return
		}
		switch r.URL.Path {
		case "/repos/github/codeql-action/releases/latest":
			w.Write([]byte(`{"tag_name":"v4.31.0"}`))
		case "/repos/actions/checkout/commits/v7.0.1":
			if r.Header.Get("Accept") != "application/vnd.github.sha" {
				http.Error(w, "bad accept", http.StatusBadRequest)
				return
			}
			w.Write([]byte("3d3c42e5aac5ba805825da76410c181273ba90b1"))
		default:
			http.NotFound(w, r)
		}
	}))
}

func TestGitHubResolverLatestVersions(t *testing.T) {
	srv := newGitHubServer(t)
	defer srv.Close()

	fallback := &fallbackStub{}
	r := &GitHubResolver{Fallback: fallback, baseURL: srv.URL, token: func() string { return "tok" }}

	got, err := r.LatestVersions(context.Background(), []string{
		"pkg:githubactions/github/codeql-action/init",
		"pkg:githubactions/someone/tags-only",
		"pkg:npm/react",
	})
	if err != nil {
		t.Fatalf("LatestVersions() error = %v", err)
	}
	want := map[string]string{
		"pkg:githubactions/github/codeql-action/init": "v4.31.0",
		"pkg:githubactions/someone/tags-only":         "v0.0.1",
		"pkg:npm/react":                               "v0.0.1",
	}
	if !maps.Equal(got, want) {
		t.Errorf("LatestVersions() = %v, want %v", got, want)
	}
	slices.Sort(fallback.got)
	if want := []string{"pkg:githubactions/someone/tags-only", "pkg:npm/react"}; !slices.Equal(fallback.got, want) {
		t.Errorf("fallback got %v, want the repo without a release and the non-action purl", fallback.got)
	}
}

func TestGitHubResolverWithoutTokenUsesFallback(t *testing.T) {
	fallback := &fallbackStub{}
	r := &GitHubResolver{Fallback: fallback, ShaFallback: shaStub{}, baseURL: "http://unused.invalid", token: func() string { return "" }}

	got, err := r.LatestVersions(context.Background(), []string{"pkg:githubactions/actions/checkout"})
	if err != nil {
		t.Fatalf("LatestVersions() error = %v", err)
	}
	if got["pkg:githubactions/actions/checkout"] != "v0.0.1" {
		t.Errorf("LatestVersions() = %v, want fallback's answer", got)
	}

	sha, err := r.ResolveSHA(context.Background(), "actions/checkout", "v7.0.1")
	if err != nil || sha != "fallbacksha" {
		t.Errorf("ResolveSHA() = %q, %v, want fallback's answer", sha, err)
	}
}

func TestGitHubResolverResolveSHA(t *testing.T) {
	srv := newGitHubServer(t)
	defer srv.Close()

	r := &GitHubResolver{baseURL: srv.URL, token: func() string { return "tok" }}
	sha, err := r.ResolveSHA(context.Background(), "actions/checkout", "v7.0.1")
	if err != nil {
		t.Fatalf("ResolveSHA() error = %v", err)
	}
	if sha != "3d3c42e5aac5ba805825da76410c181273ba90b1" {
		t.Errorf("ResolveSHA() = %q", sha)
	}
}
