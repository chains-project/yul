package resolver

import (
	"context"
	"errors"
	"testing"

	"github.com/git-pkgs/enrichment"
)

type enrichmentClientStub struct {
	result map[string]*enrichment.PackageInfo
	err    error
}

func (c *enrichmentClientStub) BulkLookup(context.Context, []string) (map[string]*enrichment.PackageInfo, error) {
	return c.result, c.err
}

func (c *enrichmentClientStub) GetVersions(context.Context, string) ([]enrichment.VersionInfo, error) {
	return nil, nil
}

func (c *enrichmentClientStub) GetVersion(context.Context, string) (*enrichment.VersionInfo, error) {
	return nil, nil
}

func TestEnrichmentResolverLatestVersions(t *testing.T) {
	client := &enrichmentClientStub{result: map[string]*enrichment.PackageInfo{
		"pkg:npm/current": {LatestVersion: "2.0.0"},
		"pkg:npm/empty":   {},
		"pkg:npm/missing": nil,
	}}
	resolver := &EnrichmentResolver{client: client, timeout: defaultTimeout}

	got, err := resolver.LatestVersions(context.Background(), []string{
		"pkg:npm/current",
		"pkg:npm/empty",
		"pkg:npm/missing",
	})
	if err != nil {
		t.Fatalf("LatestVersions() error = %v", err)
	}
	if len(got) != 1 || got["pkg:npm/current"] != "2.0.0" {
		t.Fatalf("LatestVersions() = %#v, want only current package", got)
	}
}

func TestEnrichmentResolverLatestVersionsWrapsError(t *testing.T) {
	client := &enrichmentClientStub{err: errors.New("lookup failed")}
	resolver := &EnrichmentResolver{client: client, timeout: defaultTimeout}

	if _, err := resolver.LatestVersions(context.Background(), []string{"pkg:npm/example"}); err == nil {
		t.Fatal("LatestVersions() error = nil")
	}
}
