package maven

import (
	"context"
	"errors"
	"fmt"
	"sync/atomic"
	"testing"

	"github.com/git-pkgs/enrichment"
	"github.com/git-pkgs/registries"
)

// fakeEnrichment is a minimal enrichment.Client whose GetVersions is
// driven by a scripted function per PURL, so tests can simulate a flaky
// Solr response (not-found once, found on a later call).
type fakeEnrichment struct {
	getVersions func(purl string) ([]enrichment.VersionInfo, error)
	gotPURLs    []string
}

func (f *fakeEnrichment) GetVersions(_ context.Context, purl string) ([]enrichment.VersionInfo, error) {
	f.gotPURLs = append(f.gotPURLs, purl)
	return f.getVersions(purl)
}

func (f *fakeEnrichment) BulkLookup(context.Context, []string) (map[string]*enrichment.PackageInfo, error) {
	return nil, nil
}

func (f *fakeEnrichment) GetVersion(context.Context, string) (*enrichment.VersionInfo, error) {
	return nil, nil
}

func newTestChecker(f *fakeEnrichment) *RegistryExistenceChecker {
	return &RegistryExistenceChecker{client: f}
}

func staticVersions(byPURL map[string][]enrichment.VersionInfo) func(string) ([]enrichment.VersionInfo, error) {
	return func(purl string) ([]enrichment.VersionInfo, error) {
		return byPURL[purl], nil
	}
}

func TestRegistryExistenceRealCoordinateAndVersion(t *testing.T) {
	f := &fakeEnrichment{getVersions: staticVersions(map[string][]enrichment.VersionInfo{
		"pkg:maven/com.google.guava/guava": {{Number: "32.1.3-jre"}, {Number: "33.0.0-jre"}},
	})}

	ex, err := newTestChecker(f).Existence(context.Background(), "com.google.guava", "guava", "33.0.0-jre")
	if err != nil {
		t.Fatalf("Existence() error = %v", err)
	}
	if len(f.gotPURLs) != 1 || f.gotPURLs[0] != "pkg:maven/com.google.guava/guava" {
		t.Fatalf("queried %v, want a single call with the version-less coordinate PURL", f.gotPURLs)
	}
	if !ex.Package || !ex.Version {
		t.Fatalf("Existence() = %+v, want Package and Version both true", ex)
	}
}

func TestRegistryExistenceNoVersionQueried(t *testing.T) {
	f := &fakeEnrichment{getVersions: staticVersions(map[string][]enrichment.VersionInfo{
		"pkg:maven/com.google.guava/guava": {{Number: "33.0.0-jre"}},
	})}

	ex, err := newTestChecker(f).Existence(context.Background(), "com.google.guava", "guava", "")
	if err != nil {
		t.Fatalf("Existence() error = %v", err)
	}
	if !ex.Package {
		t.Fatalf("Existence() = %+v, want Package true", ex)
	}
}

func TestRegistryExistenceEmptyVersionListDoesNotFlag(t *testing.T) {
	f := &fakeEnrichment{getVersions: staticVersions(map[string][]enrichment.VersionInfo{
		"pkg:maven/com.example/weird": {},
	})}

	ex, err := newTestChecker(f).Existence(context.Background(), "com.example", "weird", "1.0.0")
	if err != nil {
		t.Fatalf("Existence() error = %v", err)
	}
	if !ex.Package || !ex.Version {
		t.Fatalf("Existence() = %+v, want both true (empty list is not proof the version is missing)", ex)
	}
}

func TestRegistryExistenceMissingCoordinate(t *testing.T) {
	f := &fakeEnrichment{getVersions: func(string) ([]enrichment.VersionInfo, error) {
		return nil, fmt.Errorf("maven: package com.example:invented not found: %w", registries.ErrNotFound)
	}}

	ex, err := newTestChecker(f).Existence(context.Background(), "com.example", "invented", "1.0.0")
	if err != nil {
		t.Fatalf("Existence() error = %v, want nil for a confirmed-missing coordinate", err)
	}
	if ex.Package {
		t.Fatalf("Existence() = %+v, want Package false", ex)
	}
	if len(f.gotPURLs) != existenceRetries+1 {
		t.Fatalf("got %d calls, want %d (a consistent not-found is retried before being trusted)", len(f.gotPURLs), existenceRetries+1)
	}
}

func TestRegistryExistenceInconclusive(t *testing.T) {
	netErr := errors.New("context deadline exceeded")
	f := &fakeEnrichment{getVersions: func(string) ([]enrichment.VersionInfo, error) {
		return nil, netErr
	}}

	_, err := newTestChecker(f).Existence(context.Background(), "com.example", "lib", "1.0.0")
	if !errors.Is(err, netErr) {
		t.Fatalf("Existence() error = %v, want the underlying error propagated", err)
	}
	if len(f.gotPURLs) != 1 {
		t.Fatalf("got %d calls, want 1 (a non-ErrNotFound error fails open immediately, no retry)", len(f.gotPURLs))
	}
}

// TestRegistryExistenceRetryRecoversFromTransientUnknownVersion reproduces
// the false positive seen against real Maven Central: Solr's search index
// hasn't caught up with a just-published version yet, so the first
// GetVersions call comes back without it, and a later call does have it -
// without the version ever having been unpublished.
func TestRegistryExistenceRetryRecoversFromTransientUnknownVersion(t *testing.T) {
	var calls atomic.Int32
	f := &fakeEnrichment{getVersions: func(string) ([]enrichment.VersionInfo, error) {
		if calls.Add(1) == 1 {
			return []enrichment.VersionInfo{{Number: "2.1.5"}}, nil // index lag: 2.2.9 missing
		}
		return []enrichment.VersionInfo{{Number: "2.1.5"}, {Number: "2.2.9"}}, nil
	}}

	ex, err := newTestChecker(f).Existence(context.Background(), "org.apache.mina", "mina-core", "2.2.9")
	if err != nil {
		t.Fatalf("Existence() error = %v", err)
	}
	if !ex.Package || !ex.Version {
		t.Fatalf("Existence() = %+v, want both true - the retry should have recovered", ex)
	}
	if calls.Load() < 2 {
		t.Fatalf("got %d calls, want at least 2 (the retry)", calls.Load())
	}
}

func TestRegistryExistenceUnknownVersionConfirmedAfterRetries(t *testing.T) {
	f := &fakeEnrichment{getVersions: staticVersions(map[string][]enrichment.VersionInfo{
		"pkg:maven/com.google.guava/guava": {{Number: "33.0.0-jre"}},
	})}

	ex, err := newTestChecker(f).Existence(context.Background(), "com.google.guava", "guava", "99.0.0")
	if err != nil {
		t.Fatalf("Existence() error = %v", err)
	}
	if !ex.Package || ex.Version {
		t.Fatalf("Existence() = %+v, want Package true, Version false", ex)
	}
	if want := existenceRetries + 1; len(f.gotPURLs) != want {
		t.Fatalf("got %d calls, want %d (initial + retries before trusting the version is missing)", len(f.gotPURLs), want)
	}
}
