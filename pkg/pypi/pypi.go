package pypi

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

type Resolver struct{}

type pypiResponse struct {
	Info struct {
		Version string `json:"version"`
	} `json:"info"`
}

// LatestVersion fetches the current release version for a package from
// PyPI's JSON API (https://pypi.org/pypi/<name>/json), which always
// reflects the latest non-yanked release in info.version.
func (Resolver) LatestVersion(name string) (string, error) {
	url := fmt.Sprintf("https://pypi.org/pypi/%s/json", name)

	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Get(url)
	if err != nil {
		return "", fmt.Errorf("fetching package metadata: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("pypi returned %s for %s", resp.Status, name)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("reading response: %w", err)
	}

	var parsed pypiResponse
	if err := json.Unmarshal(body, &parsed); err != nil {
		return "", fmt.Errorf("parsing pypi response: %w", err)
	}

	if parsed.Info.Version == "" {
		return "", fmt.Errorf("no version found for %s", name)
	}
	return parsed.Info.Version, nil
}