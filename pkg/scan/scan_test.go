package scan

import (
	"context"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/chains-project/yul/pkg/maven"
	"github.com/chains-project/yul/pkg/npm"
	"github.com/chains-project/yul/pkg/util/manifestchecker"
)

type stubResolver map[string]string

func (r stubResolver) LatestVersions(context.Context, []string) (map[string]string, error) {
	return r, nil
}

const pom = `<project>
  <dependencies>
    <dependency>
      <groupId>com.squareup.okhttp3</groupId>
      <artifactId>okhttp</artifactId>
      <version>4.9.0</version>
    </dependency>
  </dependencies>
</project>`

const pkgJSON = `{"dependencies":{"left-pad":"1.0.0"}}`

func writeFile(t *testing.T, path, content string) {
	t.Helper()
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, []byte(content), 0o644); err != nil {
		t.Fatal(err)
	}
}

func TestDirFindsOutdatedPinsAcrossEcosystems(t *testing.T) {
	root := t.TempDir()
	writeFile(t, filepath.Join(root, "pom.xml"), pom)
	writeFile(t, filepath.Join(root, "package.json"), pkgJSON)
	writeFile(t, filepath.Join(root, "node_modules", "dep", "package.json"), pkgJSON)

	res := stubResolver{
		"pkg:maven/com.squareup.okhttp3/okhttp": "4.12.0",
		"pkg:npm/left-pad":                      "1.3.0",
	}
	checkers := []manifestchecker.ManifestChecker{
		maven.Checker{Resolver: res},
		npm.Checker{Resolver: res},
	}

	findings, err := Dir(root, checkers)
	if err != nil {
		t.Fatal(err)
	}
	if len(findings) != 2 {
		t.Fatalf("got %d findings, want 2: %+v", len(findings), findings)
	}
	byFile := map[string]Finding{}
	for _, f := range findings {
		byFile[f.File] = f
	}
	if f, ok := byFile["pom.xml"]; !ok || f.Latest != "4.12.0" {
		t.Errorf("pom.xml finding = %+v", f)
	}
	if f, ok := byFile["package.json"]; !ok || f.Latest != "1.3.0" {
		t.Errorf("package.json finding = %+v", f)
	}
	if _, ok := byFile[filepath.Join("node_modules", "dep", "package.json")]; ok {
		t.Error("node_modules should be skipped")
	}
}

func TestDirSkipsUpToDatePins(t *testing.T) {
	root := t.TempDir()
	writeFile(t, filepath.Join(root, "pom.xml"), pom)

	res := stubResolver{"pkg:maven/com.squareup.okhttp3/okhttp": "4.9.0"}
	findings, err := Dir(root, []manifestchecker.ManifestChecker{maven.Checker{Resolver: res}})
	if err != nil {
		t.Fatal(err)
	}
	if len(findings) != 0 {
		t.Fatalf("got %d findings, want 0: %+v", len(findings), findings)
	}
}

func TestHashChangesWhenManifestContentChanges(t *testing.T) {
	root := t.TempDir()
	writeFile(t, filepath.Join(root, "pom.xml"), pom)
	checkers := []manifestchecker.ManifestChecker{maven.Checker{}}

	before, err := Hash(root, checkers)
	if err != nil {
		t.Fatal(err)
	}

	// Simulate a manifest edited by hand, outside the PreToolUse hook: the
	// hash must change so a stale cache doesn't get reused for it.
	writeFile(t, filepath.Join(root, "pom.xml"), strings.Replace(pom, "4.9.0", "4.8.0", 1))

	after, err := Hash(root, checkers)
	if err != nil {
		t.Fatal(err)
	}
	if before == after {
		t.Fatal("Hash() did not change after manifest content changed")
	}

	// Re-hashing unchanged content must be stable and match a fresh scan.
	repeat, err := Hash(root, checkers)
	if err != nil {
		t.Fatal(err)
	}
	if repeat != after {
		t.Fatalf("Hash() is not stable across calls: %q != %q", repeat, after)
	}
}
