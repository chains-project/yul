// Package resolver defines the interface ecosystem checkers use to resolve
// the latest released version of a package, so tests can inject a fake
// implementation instead of making real network requests.
package resolver

import "context"

// Resolver resolves the latest released version for packages identified by
// Package URL (PURL), e.g. "pkg:npm/lodash" or "pkg:pypi/requests". A PURL
// missing from the returned map has no resolvable latest version.
type Resolver interface {
	LatestVersions(ctx context.Context, purls []string) (map[string]string, error)
}
