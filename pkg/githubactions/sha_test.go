package githubactions

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestGitHubShaResolverResolvesSha(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if want := "/repos/actions/checkout/commits/v4.2.1"; r.URL.Path != want {
			t.Errorf("request path = %q, want %q", r.URL.Path, want)
		}
		if got := r.Header.Get("User-Agent"); got != "yul" {
			t.Errorf("User-Agent = %q, want yul", got)
		}
		_, _ = w.Write([]byte("8e8c483db84b4bee98b60c0593521ed34d9990e8"))
	}))
	defer srv.Close()

	res := GitHubShaResolver{Client: srv.Client(), baseURL: srv.URL}
	sha, err := res.ResolveSHA(context.Background(), "actions/checkout", "v4.2.1")
	if err != nil {
		t.Fatalf("ResolveSHA() error = %v", err)
	}
	if want := "8e8c483db84b4bee98b60c0593521ed34d9990e8"; sha != want {
		t.Errorf("ResolveSHA() = %q, want %q", sha, want)
	}
}

func TestGitHubShaResolverErrorsOnNon200(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusNotFound)
	}))
	defer srv.Close()

	res := GitHubShaResolver{Client: srv.Client(), baseURL: srv.URL}
	if _, err := res.ResolveSHA(context.Background(), "actions/checkout", "not-a-real-tag"); err == nil {
		t.Fatal("ResolveSHA() returned nil error, want an error on a 404")
	}
}

func TestGitHubShaResolverErrorsOnEmptySha(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(http.ResponseWriter, *http.Request) {}))
	defer srv.Close()

	res := GitHubShaResolver{Client: srv.Client(), baseURL: srv.URL}
	if _, err := res.ResolveSHA(context.Background(), "actions/checkout", "v4.2.1"); err == nil {
		t.Fatal("ResolveSHA() returned nil error, want an error on an empty sha")
	}
}

func TestGitHubShaResolverRejectsInvalidRepository(t *testing.T) {
	res := GitHubShaResolver{}
	if _, err := res.ResolveSHA(context.Background(), "checkout", "v4.2.1"); err == nil {
		t.Fatal("ResolveSHA() returned nil error for invalid repository")
	}
}
