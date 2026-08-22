package resolver

import (
	"context"
	"fmt"
	"time"

	"github.com/git-pkgs/enrichment"
)

// defaultTimeout bounds every enrichment lookup so the hook's own client
// timeout stays comfortably under Claude Code's PreToolUse hook timeout,
// regardless of what enrichment's underlying HTTP client defaults to.
const defaultTimeout = 10 * time.Second

// EnrichmentResolver resolves latest versions through git-pkgs/enrichment.
// The enrichment client owns routing between ecosyste.ms and direct registry
// lookups, including repository_url qualifiers and direct-mode configuration.
type EnrichmentResolver struct {
	client  enrichment.Client
	timeout time.Duration
}

// NewEnrichmentResolver builds a Resolver using enrichment's configured
// backend selection.
func NewEnrichmentResolver() (*EnrichmentResolver, error) {
	client, err := enrichment.NewClient(enrichment.WithUserAgent("yul"))
	if err != nil {
		return nil, fmt.Errorf("creating enrichment client: %w", err)
	}
	return &EnrichmentResolver{client: client, timeout: defaultTimeout}, nil
}

// LatestVersions looks up purls in a single bulk request and returns
// PackageInfo.LatestVersion for each one found. Purls the registry has no
// metadata for are simply absent from the result.
func (r *EnrichmentResolver) LatestVersions(ctx context.Context, purls []string) (map[string]string, error) {
	ctx, cancel := context.WithTimeout(ctx, r.timeout)
	defer cancel()

	infos, err := r.client.BulkLookup(ctx, purls)
	if err != nil {
		return nil, fmt.Errorf("looking up %d package(s): %w", len(purls), err)
	}

	latest := make(map[string]string, len(infos))
	for purl, info := range infos {
		if info != nil && info.LatestVersion != "" {
			latest[purl] = info.LatestVersion
		}
	}
	return latest, nil
}
