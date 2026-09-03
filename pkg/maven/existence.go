package maven

import (
	"context"
	"encoding/xml"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"
)

// ExistenceChecker reports what Maven Central actually publishes for a
// coordinate, so the hook can flag a hallucinated <dependency> - one whose
// groupId:artifactId the model invented, or whose <version> was never
// released - rather than one that's merely outdated.
type ExistenceChecker interface {
	// Existence looks up groupID:artifactID (and, when version is
	// non-empty, that exact version). A non-nil error means the lookup was
	// inconclusive (network, timeout, an unexpected status, unparseable
	// metadata) and must not be read as "does not exist".
	Existence(ctx context.Context, groupID, artifactID, version string) (Existence, error)
}

// Existence is what a Maven Central lookup established about a coordinate.
type Existence struct {
	// Package is true when groupID:artifactID is published.
	Package bool

	// Version is true when the queried version is in the published version
	// list. Only meaningful when a non-empty version was queried, Package
	// is true, and that list was non-empty.
	Version bool
}

const (
	// defaultExistenceTimeout bounds a single coordinate lookup, mirroring
	// resolver.EnrichmentResolver's own budget so the hook stays well
	// under Claude Code's PreToolUse timeout.
	defaultExistenceTimeout = 10 * time.Second

	mavenCentralBaseURL = "https://repo1.maven.org/maven2"

	// maxMetadataBytes caps the maven-metadata.xml read. Even artifacts
	// with thousands of releases stay well under this.
	maxMetadataBytes = 8 << 20
)

// MavenCentralExistenceChecker decides what's published by fetching a
// coordinate's maven-metadata.xml.
//
// This deliberately does not go through git-pkgs/enrichment's registry
// client: that client queries Maven Central's Solr endpoint
// (search.maven.org) first, which returns found / not-found / timeout
// inconsistently for the same coordinate and hands back paginated,
// sometimes-incomplete version lists - fine for enrichment's best-effort
// metadata, unacceptable for a hook that blocks writes. maven-metadata.xml
// is served straight off repo1.maven.org's static CDN, carries the
// complete version list in one file, and is what Maven itself resolves
// against; a 200/404 and the list it contains are authoritative and
// reproducible. It is also the path the registry client falls back to.
type MavenCentralExistenceChecker struct {
	// BaseURL overrides Maven Central's repository root, for tests. Empty
	// means the real one.
	BaseURL string

	// Client is the HTTP client to use; nil builds one bounded by
	// defaultExistenceTimeout on each call.
	Client *http.Client
}

// NewMavenCentralExistenceChecker returns a checker pointed at the real
// Maven Central.
func NewMavenCentralExistenceChecker() *MavenCentralExistenceChecker {
	return &MavenCentralExistenceChecker{}
}

type mavenMetadata struct {
	Versioning struct {
		Versions struct {
			Version []string `xml:"version"`
		} `xml:"versions"`
	} `xml:"versioning"`
}

// Existence GETs <base>/<group as path>/<artifact>/maven-metadata.xml. 404
// means the coordinate doesn't exist; 200 means it does, and its
// <versioning><versions> list is checked for version (when non-empty). Any
// other status, a transport error, or unparseable XML is returned so the
// caller can fail open.
func (c *MavenCentralExistenceChecker) Existence(ctx context.Context, groupID, artifactID, version string) (Existence, error) {
	base := c.BaseURL
	if base == "" {
		base = mavenCentralBaseURL
	}
	client := c.Client
	if client == nil {
		client = &http.Client{Timeout: defaultExistenceTimeout}
	}

	u := strings.TrimSuffix(base, "/") + "/" +
		strings.ReplaceAll(groupID, ".", "/") + "/" + artifactID + "/maven-metadata.xml"

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, u, nil)
	if err != nil {
		return Existence{}, err
	}
	req.Header.Set("User-Agent", "yul")

	resp, err := client.Do(req)
	if err != nil {
		return Existence{}, err
	}
	defer resp.Body.Close()

	switch resp.StatusCode {
	case http.StatusOK:
	case http.StatusNotFound:
		_, _ = io.Copy(io.Discard, resp.Body)
		return Existence{Package: false}, nil
	default:
		_, _ = io.Copy(io.Discard, resp.Body)
		return Existence{}, fmt.Errorf("maven central: %s for %s:%s", resp.Status, groupID, artifactID)
	}

	body, err := io.ReadAll(io.LimitReader(resp.Body, maxMetadataBytes))
	if err != nil {
		return Existence{}, err
	}

	var meta mavenMetadata
	if err := xml.Unmarshal(body, &meta); err != nil {
		return Existence{}, fmt.Errorf("maven central: parsing metadata for %s:%s: %w", groupID, artifactID, err)
	}

	ex := Existence{Package: true}
	versions := meta.Versioning.Versions.Version
	if version == "" || len(versions) == 0 {
		// Nothing to check against, or an empty list we shouldn't trust as
		// proof the version is missing - treat the version as unconfirmed
		// but present so it isn't flagged.
		ex.Version = true
		return ex, nil
	}
	for _, v := range versions {
		if v == version {
			ex.Version = true
			break
		}
	}
	return ex, nil
}
