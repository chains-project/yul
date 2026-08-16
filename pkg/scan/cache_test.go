package scan

import (
	"path/filepath"
	"testing"
	"time"
)

func TestCacheFresh(t *testing.T) {
	now := time.Date(2026, 1, 8, 0, 0, 0, 0, time.UTC)
	tests := []struct {
		name    string
		cache   Cache
		version string
		ttl     time.Duration
		hash    string
		want    bool
	}{
		{"fresh", Cache{YulVersion: "1.0.0", ManifestsHash: "h1", ScannedAt: now.Add(-time.Hour)}, "1.0.0", 24 * time.Hour, "h1", true},
		{"expired", Cache{YulVersion: "1.0.0", ManifestsHash: "h1", ScannedAt: now.Add(-48 * time.Hour)}, "1.0.0", 24 * time.Hour, "h1", false},
		{"version bump forces rescan", Cache{YulVersion: "1.0.0", ManifestsHash: "h1", ScannedAt: now}, "1.0.1", 24 * time.Hour, "h1", false},
		{"manifest changed forces rescan", Cache{YulVersion: "1.0.0", ManifestsHash: "h1", ScannedAt: now}, "1.0.0", 24 * time.Hour, "h2", false},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			if got := test.cache.Fresh(test.version, test.ttl, now, test.hash); got != test.want {
				t.Errorf("Fresh() = %v, want %v", got, test.want)
			}
		})
	}
}

func TestCacheRoundTrip(t *testing.T) {
	dir := t.TempDir()
	path, err := CachePath(dir, "/some/project")
	if err != nil {
		t.Fatal(err)
	}

	if _, ok := LoadCache(path); ok {
		t.Fatal("expected no cache before it's saved")
	}

	want := Cache{
		YulVersion: "1.2.3",
		ScannedAt:  time.Now().UTC().Truncate(time.Second),
		ProjectDir: "/some/project",
		Findings: []Finding{
			{File: "pom.xml"},
		},
	}
	if err := SaveCache(path, want); err != nil {
		t.Fatal(err)
	}

	got, ok := LoadCache(path)
	if !ok {
		t.Fatal("expected cache to load after saving")
	}
	if got.YulVersion != want.YulVersion || !got.ScannedAt.Equal(want.ScannedAt) || len(got.Findings) != 1 {
		t.Fatalf("LoadCache() = %+v, want %+v", got, want)
	}
}

func TestCachePathNamespacesByProjectDir(t *testing.T) {
	dir := t.TempDir()
	a, err := CachePath(dir, "/project/a")
	if err != nil {
		t.Fatal(err)
	}
	b, err := CachePath(dir, "/project/b")
	if err != nil {
		t.Fatal(err)
	}
	if a == b {
		t.Fatal("expected different projects to get different cache paths")
	}
	if filepath.Dir(a) != filepath.Join(dir, "yul", "scan") {
		t.Fatalf("CachePath() = %q, want it under %q", a, filepath.Join(dir, "yul", "scan"))
	}
}
