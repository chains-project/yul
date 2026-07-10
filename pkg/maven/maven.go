// Package maven resolves the latest released version of a Maven artifact
// by reading maven-metadata.xml from Maven Central.
package maven

import (
	"encoding/xml"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"
)

type Resolver struct{}

type metadata struct {
	Versioning struct {
		Release string `xml:"release"`
		Latest  string `xml:"latest"`
	} `xml:"versioning"`
}

// LatestVersion fetches the release version for a Maven groupId:artifactId
// from repo1.maven.org's maven-metadata.xml.
func (Resolver) LatestVersion(groupID, artifactID string) (string, error) {
	groupPath := strings.ReplaceAll(groupID, ".", "/")
	url := fmt.Sprintf("https://repo1.maven.org/maven2/%s/%s/maven-metadata.xml", groupPath, artifactID)

	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Get(url)
	if err != nil {
		return "", fmt.Errorf("fetching maven-metadata.xml: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("maven central returned %s for %s:%s", resp.Status, groupID, artifactID)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("reading response: %w", err)
	}

	var md metadata
	if err := xml.Unmarshal(body, &md); err != nil {
		return "", fmt.Errorf("parsing maven-metadata.xml: %w", err)
	}

	if md.Versioning.Release != "" {
		return md.Versioning.Release, nil
	}
	if md.Versioning.Latest != "" {
		return md.Versioning.Latest, nil
	}
	return "", fmt.Errorf("no release version found for %s:%s", groupID, artifactID)
}
