package githubactions

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strings"
	"time"
)

type ShaResolver interface {
	// ResolveSHA returns the commit SHA that tag points to in repo (an
	// "owner/name" GitHub repository, not an action's possibly-nested
	// name - see repoOf).
	ResolveSHA(ctx context.Context, repo, tag string) (string, error)
}

// defaultShaTimeout bounds a single GitHub API lookup, mirroring
// resolver.EnrichmentResolver's defaultTimeout.
const defaultShaTimeout = 10 * time.Second

const githubAPIBaseURL = "https://api.github.com"

// GitHubShaResolver resolves tags to commit SHAs through the GitHub REST
// API (GET /repos/{repo}/commits/{tag}), which reports the commit a tag
// points to whether it's lightweight or annotated. Requests are
// unauthenticated unless GITHUB_TOKEN is set, in which case it's sent to
// raise the otherwise low unauthenticated rate limit.
type GitHubShaResolver struct {
	// Client is the HTTP client to use; a zero-value resolver builds one
	// with defaultShaTimeout on first use.
	Client *http.Client

	// baseURL overrides githubAPIBaseURL; unexported, for tests only.
	baseURL string
}

func (g GitHubShaResolver) ResolveSHA(ctx context.Context, repo, tag string) (string, error) {
	client := g.Client
	if client == nil {
		client = &http.Client{Timeout: defaultShaTimeout}
	}

	base := g.baseURL
	if base == "" {
		base = githubAPIBaseURL
	}
	url := fmt.Sprintf("%s/repos/%s/commits/%s", base, repo, tag)
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return "", err
	}
	req.Header.Set("Accept", "application/vnd.github+json")
	req.Header.Set("User-Agent", "yul")
	if token := os.Getenv("GITHUB_TOKEN"); token != "" {
		req.Header.Set("Authorization", "Bearer "+token)
	}

	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("github API %s: status %d", url, resp.StatusCode)
	}

	var body struct {
		SHA string `json:"sha"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&body); err != nil {
		return "", err
	}
	if body.SHA == "" {
		return "", fmt.Errorf("github API %s: response had no sha", url)
	}
	return body.SHA, nil
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
