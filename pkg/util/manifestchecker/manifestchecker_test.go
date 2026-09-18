package manifestchecker

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/chains-project/yul/pkg/util/mismatch"
)

type lockfileAwareChecker struct{ names []string }

func (lockfileAwareChecker) Filename() string          { return "manifest.json" }
func (c lockfileAwareChecker) LockfileNames() []string { return c.names }
func (lockfileAwareChecker) Check(before, after string, hasLockfile bool) ([]mismatch.Mismatch, error) {
	return nil, nil
}

type unawareChecker struct{}

func (unawareChecker) Filename() string { return "manifest.json" }
func (unawareChecker) Check(before, after string, hasLockfile bool) ([]mismatch.Mismatch, error) {
	return nil, nil
}

func TestHasLockfileReportsTrueWhenACandidateExists(t *testing.T) {
	dir := t.TempDir()
	if err := os.WriteFile(filepath.Join(dir, "b.lock"), nil, 0o644); err != nil {
		t.Fatal(err)
	}
	checker := lockfileAwareChecker{names: []string{"a.lock", "b.lock"}}
	if !HasLockfile(dir, checker) {
		t.Fatal("HasLockfile() = false, want true")
	}
}

func TestHasLockfileReportsFalseWhenNoCandidateExists(t *testing.T) {
	dir := t.TempDir()
	checker := lockfileAwareChecker{names: []string{"a.lock", "b.lock"}}
	if HasLockfile(dir, checker) {
		t.Fatal("HasLockfile() = true, want false")
	}
}

func TestHasLockfileReportsTrueForACheckerThatDoesNotImplementLockfileAware(t *testing.T) {
	dir := t.TempDir()
	if HasLockfile(dir, unawareChecker{}) != true {
		t.Fatal("HasLockfile() = false, want true for a checker with no lockfile convention")
	}
}
