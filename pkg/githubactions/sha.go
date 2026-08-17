package githubactions

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"strings"
	"time"

	githubforge "github.com/git-pkgs/forge/github"
)

// ShaResolver resolves GitHub refs to commit SHAs for suggested immutable
// action pins.
type ShaResolver interface {
	// ResolveSHA returns the commit SHA that tag points to in repo (an
	// "owner/name" GitHub repository, not an action's possibly-nested
	// name - see repoOf).
	ResolveSHA(ctx context.Context, repo, tag string) (string, error)
}

// defaultShaTimeout bounds a single GitHub API lookup, mirroring
// resolver.EnrichmentResolver's defaultTimeout.
const defaultShaTimeout = 10 * time.Second

// GitHubShaResolver resolves tags through git-pkgs/forge. Requests are
// unauthenticated unless GITHUB_TOKEN is set.
type GitHubShaResolver struct {
	// Client is the HTTP client to use; a zero-value resolver builds one
	// with defaultShaTimeout on first use.
	Client *http.Client

	// baseURL overrides forge's public GitHub API URL for tests.
	baseURL string
}

type userAgentTransport struct {
	base http.RoundTripper
}

// RoundTrip sends req with yul's User-Agent without mutating the caller's
// request.
func (t userAgentTransport) RoundTrip(req *http.Request) (*http.Response, error) {
	clone := req.Clone(req.Context())
	clone.Header.Set("User-Agent", "yul")
	return t.base.RoundTrip(clone)
}

// ResolveSHA returns the full commit SHA for tag in an owner/repo GitHub
// repository.
func (g GitHubShaResolver) ResolveSHA(ctx context.Context, repo, tag string) (string, error) {
	client := g.Client
	if client == nil {
		client = &http.Client{Timeout: defaultShaTimeout}
	}
	httpClient := *client
	transport := httpClient.Transport
	if transport == nil {
		transport = http.DefaultTransport
	}
	httpClient.Transport = userAgentTransport{base: transport}

	base := g.baseURL
	if base == "" {
		base = githubforge.DefaultAPIBaseURL
	}
	owner, name, ok := strings.Cut(repo, "/")
	if !ok || owner == "" || name == "" || strings.Contains(name, "/") {
		return "", fmt.Errorf("invalid GitHub repository %q", repo)
	}
	resolver, err := githubforge.NewCommitResolverWithBase(base, os.Getenv("GITHUB_TOKEN"), &httpClient)
	if err != nil {
		return "", fmt.Errorf("creating GitHub commit resolver: %w", err)
	}
	return resolver.ResolveCommit(ctx, owner, name, tag)
}

// repoOf reduces an action name to the "owner/repo" GitHub repository it
// lives in, stripping any subpath (e.g. "actions/cache/restore" ->
// "actions/cache", a subdirectory action in the actions/cache repo).
func repoOf(name string) string {
	parts := strings.SplitN(name, "/", 3)
	if len(parts) < 2 {
		return name
	}
	return parts[0] + "/" + parts[1]
}
