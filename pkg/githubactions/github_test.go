package githubactions

import (
	"context"
	"slices"
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
		latest[p] = "v0.0.1"
	}
	return latest, nil
}

type shaStub struct{}

func (shaStub) ResolveSHA(context.Context, string, string) (string, error) {
	return "fallbacksha", nil
}

// liveToken skips t unless a GitHub token is available: without one,
// GitHubResolver never calls GitHub, and GitHub only allows 60
// unauthenticated requests an hour anyway.
func liveToken(t *testing.T) func() string {
	t.Helper()
	token := githubToken()
	if token == "" {
		t.Skip("no GitHub token (GITHUB_TOKEN, GH_TOKEN, or gh auth token)")
	}
	return func() string { return token }
}

// TestGitHubResolverLatestVersions queries GitHub's API. The latest
// release moves, so it's only checked to be at least one already
// released.
func TestGitHubResolverLatestVersions(t *testing.T) {
	fallback := &fallbackStub{}
	r := &GitHubResolver{Fallback: fallback, token: liveToken(t)}

	got, err := r.LatestVersions(context.Background(), []string{
		"pkg:githubactions/actions/checkout",
		"pkg:githubactions/github/codeql-action/init",
		"pkg:githubactions/chains-project/yul-test-repo-that-does-not-exist",
		"pkg:npm/react",
	})
	if err != nil {
		t.Fatalf("LatestVersions() error = %v", err)
	}

	for purl, atLeast := range map[string]string{
		"pkg:githubactions/actions/checkout":          "v4.0.0",
		"pkg:githubactions/github/codeql-action/init": "v3.0.0",
	} {
		if v := got[purl]; vers.Compare(v, atLeast) < 0 {
			t.Errorf("%s: latest %q is older than %q", purl, v, atLeast)
		}
	}

	slices.Sort(fallback.got)
	if want := []string{"pkg:githubactions/chains-project/yul-test-repo-that-does-not-exist", "pkg:npm/react"}; !slices.Equal(fallback.got, want) {
		t.Errorf("fallback got %v, want the repo without a release and the non-action purl", fallback.got)
	}
}

func TestGitHubResolverResolveSHA(t *testing.T) {
	r := &GitHubResolver{token: liveToken(t)}
	sha, err := r.ResolveSHA(context.Background(), "actions/checkout", "v4.0.0")
	if err != nil {
		t.Fatalf("ResolveSHA() error = %v", err)
	}
	if sha != "1e31de5234b9f8995739874a8ce0492dc87873e2" {
		t.Errorf("ResolveSHA() = %q", sha)
	}
}

func TestGitHubResolverWithoutTokenUsesFallback(t *testing.T) {
	fallback := &fallbackStub{}
	r := &GitHubResolver{Fallback: fallback, ShaFallback: shaStub{}, token: func() string { return "" }}

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
