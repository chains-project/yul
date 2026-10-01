package githubactions

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"maps"
	"net/http"
	"net/url"
	"os"
	"os/exec"
	"strings"
	"sync"

	"github.com/chains-project/yul/pkg/util/resolver"
	"github.com/git-pkgs/purl"
	"github.com/git-pkgs/vers"
)

const githubAPI = "https://api.github.com"

// githubToken finds a token for GitHub's API in GITHUB_TOKEN, GH_TOKEN, or
// `gh auth token`, looked up once per process and only when first needed.
var githubToken = sync.OnceValue(func() string {
	for _, k := range []string{"GITHUB_TOKEN", "GH_TOKEN"} {
		if t := os.Getenv(k); t != "" {
			return t
		}
	}
	out, err := exec.Command("gh", "auth", "token").Output()
	if err != nil {
		return ""
	}
	return strings.TrimSpace(string(out))
})

// GitHubResolver resolves an action's latest release, and the commit SHA
// that release's tag points to, straight from GitHub's API. GitHub allows
// only 60 unauthenticated requests an hour, so without a token it defers
// to Fallback / ShaFallback (ecosyste.ms) instead; Fallback also covers
// any repo whose latest release lookup fails, e.g. one that only pushes
// tags and never publishes a release, and any purl that isn't a GitHub
// Action at all.
type GitHubResolver struct {
	Fallback    resolver.Resolver
	ShaFallback ShaResolver

	// Client is the HTTP client to use; nil means http.DefaultClient.
	Client *http.Client

	// token overrides githubToken for tests.
	token func() string
}

func (r *GitHubResolver) LatestVersions(ctx context.Context, purls []string) (map[string]string, error) {
	token := r.getToken()
	if token == "" {
		return r.fallback(ctx, purls)
	}

	var (
		mu       sync.Mutex
		wg       sync.WaitGroup
		latest   = make(map[string]string, len(purls))
		fallback []string
	)
	for _, p := range purls {
		if !strings.HasPrefix(p, "pkg:githubactions/") {
			fallback = append(fallback, p)
			continue
		}
		wg.Go(func() {
			tag, err := r.latestRelease(ctx, token, p)
			mu.Lock()
			defer mu.Unlock()
			if err != nil || tag == "" {
				fallback = append(fallback, p)
				return
			}
			latest[p] = tag
		})
	}
	wg.Wait()

	if len(fallback) > 0 {
		got, err := r.fallback(ctx, fallback)
		if err != nil {
			return nil, err
		}
		maps.Copy(latest, got)
	}
	return latest, nil
}

// ResolveSHA returns the commit SHA tag points to in repo, dereferencing
// annotated tags.
func (r *GitHubResolver) ResolveSHA(ctx context.Context, repo, tag string) (string, error) {
	token := r.getToken()
	if token == "" {
		if r.ShaFallback == nil {
			return "", fmt.Errorf("no GitHub token and no fallback SHA resolver")
		}
		return r.ShaFallback.ResolveSHA(ctx, repo, tag)
	}

	// A rejected token (e.g. a stale GH_TOKEN) must not disable pinning, so
	// any failure here defers to the fallback just like having no token.
	sha, err := r.githubSHA(ctx, token, repo, tag)
	if err != nil && r.ShaFallback != nil {
		return r.ShaFallback.ResolveSHA(ctx, repo, tag)
	}
	return sha, err
}

func (r *GitHubResolver) githubSHA(ctx context.Context, token, repo, tag string) (string, error) {
	resp, err := r.get(ctx, token, "/repos/"+repo+"/commits/"+url.PathEscape(tag), "application/vnd.github.sha")
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()
	sha, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}
	return strings.TrimSpace(string(sha)), nil
}

// latestRelease returns the highest version-like tag among the recent
// releases (never drafts or pre-releases) of the repo p's action lives in.
// It doesn't use releases/latest, since a repo can mark a release that
// isn't the action's at all as latest (github/codeql-action marks its
// codeql-bundle-v2.x releases).
// e.g. https://api.github.com/repos/actions/checkout/releases?per_page=100
func (r *GitHubResolver) latestRelease(ctx context.Context, token, p string) (string, error) {
	parsed, err := purl.Parse(p)
	if err != nil {
		return "", err
	}
	resp, err := r.get(ctx, token, "/repos/"+repoOf(parsed.FullName())+"/releases?per_page=100", "application/vnd.github+json")
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()
	var releases []struct {
		TagName    string `json:"tag_name"`
		Draft      bool   `json:"draft"`
		Prerelease bool   `json:"prerelease"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&releases); err != nil {
		return "", err
	}
	var latest string
	for _, release := range releases {
		if release.Draft || release.Prerelease || !looksLikeVersion(release.TagName) {
			continue
		}
		if latest == "" || vers.Compare(release.TagName, latest) > 0 {
			latest = release.TagName
		}
	}
	return latest, nil
}

func (r *GitHubResolver) get(ctx context.Context, token, path, accept string) (*http.Response, error) {
	ctx, cancel := context.WithTimeout(ctx, defaultShaTimeout)
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, githubAPI+path, nil)
	if err != nil {
		cancel()
		return nil, err
	}
	req.Header.Set("User-Agent", "yul")
	req.Header.Set("Accept", accept)
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("X-GitHub-Api-Version", "2022-11-28")

	client := r.Client
	if client == nil {
		client = http.DefaultClient
	}
	resp, err := client.Do(req)
	if err != nil {
		cancel()
		return nil, err
	}
	if resp.StatusCode != http.StatusOK {
		resp.Body.Close()
		cancel()
		return nil, fmt.Errorf("fetching %s: unexpected status %d", githubAPI+path, resp.StatusCode)
	}
	resp.Body = cancelOnClose{resp.Body, cancel}
	return resp, nil
}

// cancelOnClose releases a request's timeout once its body is read.
type cancelOnClose struct {
	io.ReadCloser
	cancel context.CancelFunc
}

func (c cancelOnClose) Close() error {
	defer c.cancel()
	return c.ReadCloser.Close()
}

func (r *GitHubResolver) getToken() string {
	if r.token != nil {
		return r.token()
	}
	return githubToken()
}

func (r *GitHubResolver) fallback(ctx context.Context, purls []string) (map[string]string, error) {
	if r.Fallback == nil {
		return map[string]string{}, nil
	}
	return r.Fallback.LatestVersions(ctx, purls)
}
