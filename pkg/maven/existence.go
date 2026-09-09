package maven

import (
	"context"
	"errors"
	"time"

	"github.com/git-pkgs/enrichment"
	"github.com/git-pkgs/registries"
)

// ExistenceChecker reports what Maven Central actually publishes for a
// coordinate, so the hook can flag a hallucinated <dependency> - one whose
// groupId:artifactId the model invented, or whose <version> was never
// released - rather than one that's merely outdated. When it reports both
// as present the caller continues with the normal outdated comparison.
type ExistenceChecker interface {
	// Existence looks up groupID:artifactID and, when version is non-empty,
	// that exact version. A non-nil error means the lookup was inconclusive
	// (network, an unexpected registry error) and must not be read as
	// "does not exist".
	Existence(ctx context.Context, groupID, artifactID, version string) (Existence, error)
}

// Existence is what a registry lookup established about a coordinate.
type Existence struct {
	// Package is true when groupID:artifactID is published.
	Package bool

	// Version is true when the queried version is in the published version
	// list. Only meaningful when a non-empty version was queried, Package
	// is true, and that list was non-empty.
	Version bool
}

const (
	// existenceRetries is how many extra times a "not found" result -
	// either the whole package or a single version - is retried before
	// it's trusted. GetVersions ultimately queries Maven Central's Solr
	// search index (core=gav), which is found/not-found inconsistent for
	// the same coordinate shortly after a new release (search indexing
	// lag) - a hook that blocks writes can't afford to read that as
	// "hallucinated".
	existenceRetries    = 1
	existenceRetryDelay = 300 * time.Millisecond
)

// RegistryExistenceChecker answers existence queries through
// git-pkgs/enrichment's direct-registry client. It is repository-aware:
// git-pkgs/manifests already puts a repository_url qualifier on the PURL
// when the pom declares <repositories>, so a dependency hosted on
// Atlassian, JitPack, Jenkins, etc. is resolved against that repository,
// not just Maven Central.
//
// git-pkgs/registries queries Maven Central's Solr endpoint
// (search.maven.org) with core=gav. Versions v0.8.1 and earlier decoded
// the wrong JSON field for that response shape, so every returned version
// came back as an empty string - fixed upstream in
// https://github.com/git-pkgs/registries/pull/82 (v0.9.1). What's left is
// Solr's own search-index lag: a just-published version, or occasionally
// the package itself, can briefly come back not-found before the index
// catches up. Existence retries a "not found" once before trusting it, to
// smooth over that gap.
//
// It imposes no timeout of its own beyond that retry budget: the call is
// bounded by the enrichment client's own retry/circuit-breaker budget and,
// ultimately, by Claude Code's PreToolUse hook timeout - a killed hook
// simply doesn't block (fail open), like any other inconclusive lookup.
type RegistryExistenceChecker struct {
	client enrichment.Client
}

// NewRegistryExistenceChecker builds a checker backed by enrichment's
// direct-registry client.
func NewRegistryExistenceChecker() *RegistryExistenceChecker {
	return &RegistryExistenceChecker{client: enrichment.NewRegistriesClient()}
}

// Existence lists the coordinate's published versions through the registry
// client. A registries.ErrNotFound is retried existenceRetries times before
// it's trusted as "the package doesn't exist"; likewise, a queried version
// absent from a non-empty list is retried (a fresh GetVersions call) before
// it's trusted as "the version doesn't exist". Any other error is returned
// immediately so the caller can fail open. An empty list is not treated as
// proof the version is missing.
func (c *RegistryExistenceChecker) Existence(ctx context.Context, groupID, artifactID, version string) (Existence, error) {
	purl := "pkg:maven/" + groupID + "/" + artifactID

	versions, notFound, err := c.getVersionsRetrying(ctx, purl)
	if err != nil {
		return Existence{}, err
	}
	if notFound {
		return Existence{Package: false}, nil
	}

	ex := Existence{Package: true}
	if version == "" || len(versions) == 0 {
		ex.Version = true
		return ex, nil
	}
	if hasVersion(versions, version) {
		ex.Version = true
		return ex, nil
	}

	// The version wasn't in the first list: retry the whole query, since
	// Solr's search-index lag is per-query, not just per-coordinate.
	for attempt := 0; attempt < existenceRetries; attempt++ {
		if err := sleep(ctx, existenceRetryDelay); err != nil {
			return Existence{}, err
		}
		vs, notFound, err := c.getVersions(ctx, purl)
		if err != nil {
			return Existence{}, err
		}
		if notFound {
			continue // package was confirmed to exist a moment ago; keep retrying the version
		}
		if hasVersion(vs, version) {
			ex.Version = true
			return ex, nil
		}
	}
	return ex, nil // confirmed missing after retries: Version stays false
}

// getVersionsRetrying calls getVersions, retrying a registries.ErrNotFound
// existenceRetries times before trusting it.
func (c *RegistryExistenceChecker) getVersionsRetrying(ctx context.Context, purl string) (versions []enrichment.VersionInfo, notFound bool, err error) {
	for attempt := 0; ; attempt++ {
		versions, notFound, err = c.getVersions(ctx, purl)
		if err != nil || !notFound {
			return versions, notFound, err
		}
		if attempt >= existenceRetries {
			return versions, notFound, err
		}
		if err := sleep(ctx, existenceRetryDelay); err != nil {
			return nil, false, err
		}
	}
}

// getVersions is a single, unretried GetVersions call. notFound reports a
// registries.ErrNotFound; any other error is returned for the caller to
// fail open on.
func (c *RegistryExistenceChecker) getVersions(ctx context.Context, purl string) (versions []enrichment.VersionInfo, notFound bool, err error) {
	vs, err := c.client.GetVersions(ctx, purl)
	if err != nil {
		if errors.Is(err, registries.ErrNotFound) {
			return nil, true, nil
		}
		return nil, false, err
	}
	return vs, false, nil
}

func hasVersion(versions []enrichment.VersionInfo, version string) bool {
	for _, v := range versions {
		if v.Number == version {
			return true
		}
	}
	return false
}

// sleep waits for d or ctx cancellation, whichever comes first.
func sleep(ctx context.Context, d time.Duration) error {
	select {
	case <-ctx.Done():
		return ctx.Err()
	case <-time.After(d):
		return nil
	}
}
