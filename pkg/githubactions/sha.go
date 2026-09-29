package githubactions

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"strings"
	"time"

	"github.com/ecosyste-ms/ecosystems-go/packages"
)

// ShaResolver resolves GitHub refs to commit SHAs for suggested immutable
// action pins.
type ShaResolver interface {
	// ResolveSHA returns the commit SHA that tag points to in repo (an
	// "owner/name" GitHub repository, not an action's possibly-nested
	// name - see repoOf).
	ResolveSHA(ctx context.Context, repo, tag string) (string, error)
}

// defaultShaTimeout bounds a single ecosyste.ms lookup, mirroring
// resolver.EnrichmentResolver's defaultTimeout.
const defaultShaTimeout = 10 * time.Second

// EcosystemsShaResolver resolves tags to commit SHAs through the sha
// ecosyste.ms already mirrors for each githubactions release, so this stays
// within the same backend and rate limits LatestVersions relies on instead
// of adding a second, GitHub-specific one.
type EcosystemsShaResolver struct {
	// Client is the HTTP client to use; a zero-value resolver builds one
	// with defaultShaTimeout on first use.
	Client *http.Client

	// baseURL overrides packages.ServerURLHTTPSPackagesEcosysteMsAPIV1 for
	// tests.
	baseURL string
}

// ecosystemsVersion is the subset of packages.ecosyste.ms's version
// response this resolver needs.
type ecosystemsVersion struct {
	Metadata struct {
		Sha string `json:"sha"`
	} `json:"metadata"`
}

// ResolveSHA returns the commit SHA ecosyste.ms recorded for repo (an
// "owner/name" GitHub repository) at tag.
func (r EcosystemsShaResolver) ResolveSHA(ctx context.Context, repo, tag string) (string, error) {
	client := r.Client
	if client == nil {
		client = &http.Client{Timeout: defaultShaTimeout}
	}

	base := r.baseURL
	if base == "" {
		base = packages.ServerURLHTTPSPackagesEcosysteMsAPIV1
	}
	reqURL := fmt.Sprintf("%s/registries/github%%20actions/packages/%s/versions/%s",
		base, url.PathEscape(repo), url.PathEscape(tag))

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, reqURL, nil)
	if err != nil {
		return "", fmt.Errorf("building request: %w", err)
	}
	req.Header.Set("User-Agent", "yul")

	resp, err := client.Do(req)
	if err != nil {
		return "", fmt.Errorf("fetching %s: %w", reqURL, err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("fetching %s: unexpected status %d", reqURL, resp.StatusCode)
	}

	var version ecosystemsVersion
	if err := json.NewDecoder(resp.Body).Decode(&version); err != nil {
		return "", fmt.Errorf("decoding response from %s: %w", reqURL, err)
	}
	if version.Metadata.Sha == "" {
		return "", fmt.Errorf("no sha in version metadata for %s@%s", repo, tag)
	}
	return version.Metadata.Sha, nil
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
