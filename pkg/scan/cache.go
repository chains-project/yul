package scan

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"os"
	"path/filepath"
	"time"
)

// Cache is the on-disk record of a project's last full scan, so repeated
// SessionStart hooks in the same project don't re-resolve every pinned
// dependency against its registry on every session.
type Cache struct {
	YulVersion    string    `json:"yul_version"`
	ManifestsHash string    `json:"manifests_hash"`
	ScannedAt     time.Time `json:"scanned_at"`
	ProjectDir    string    `json:"project_dir"`
	Findings      []Finding `json:"findings"`
}

// Fresh reports whether the cache can be reused as-is: it was written by
// the same yul build (an upgrade always forces a rescan, since a newer yul
// may resolve or parse differently), within ttl of now, and manifestsHash
// (from Hash, computed cheaply with no network calls) still matches — a
// manifest edited since the cache was written, by hand or otherwise, always
// forces a rescan regardless of ttl.
func (c Cache) Fresh(yulVersion string, ttl time.Duration, now time.Time, manifestsHash string) bool {
	return c.YulVersion == yulVersion && c.ManifestsHash == manifestsHash && now.Sub(c.ScannedAt) < ttl
}

// CachePath returns where the scan cache for projectDir lives, namespaced
// by a hash of its absolute path so multiple projects don't collide.
func CachePath(cacheHome, projectDir string) (string, error) {
	abs, err := filepath.Abs(projectDir)
	if err != nil {
		return "", err
	}
	sum := sha256.Sum256([]byte(abs))
	return filepath.Join(cacheHome, "yul", "scan", hex.EncodeToString(sum[:8])+".json"), nil
}

// LoadCache reads and parses the cache at path. A missing or corrupt cache
// is not an error: it just means there's nothing to reuse.
func LoadCache(path string) (Cache, bool) {
	raw, err := os.ReadFile(path)
	if err != nil {
		return Cache{}, false
	}
	var c Cache
	if err := json.Unmarshal(raw, &c); err != nil {
		return Cache{}, false
	}
	return c, true
}

// SaveCache writes c to path, creating parent directories as needed.
func SaveCache(path string, c Cache) error {
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return err
	}
	raw, err := json.MarshalIndent(c, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(path, raw, 0o644)
}
