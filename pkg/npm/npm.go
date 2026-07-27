// Package npm resolves the latest released version of an npm package from
// the npm registry.
package npm

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"time"
)

type Resolver struct{}

type npmResponse struct {
	DistTags struct {
		Latest string `json:"latest"`
	} `json:"dist-tags"`
}

// LatestVersion fetches the current "latest" dist-tag for a package from the
// npm registry (https://registry.npmjs.org/<name>).
func (Resolver) LatestVersion(name string) (string, error) {
	fetchURL := fmt.Sprintf("https://registry.npmjs.org/%s", url.PathEscape(name))

	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Get(fetchURL)
	if err != nil {
		return "", fmt.Errorf("fetching package metadata: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("npm registry returned %s for %s", resp.Status, name)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("reading response: %w", err)
	}

	var parsed npmResponse
	if err := json.Unmarshal(body, &parsed); err != nil {
		return "", fmt.Errorf("parsing npm registry response: %w", err)
	}

	if parsed.DistTags.Latest == "" {
		return "", fmt.Errorf("no version found for %s", name)
	}
	return parsed.DistTags.Latest, nil
}
