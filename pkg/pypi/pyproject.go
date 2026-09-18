package pypi

import (
	"context"

	"github.com/chains-project/yul/pkg/util/mismatch"
	"github.com/chains-project/yul/pkg/util/pins"
	"github.com/chains-project/yul/pkg/util/resolver"
)

// PyprojectChecker implements manifestchecker.ManifestChecker for
// pyproject.toml, covering both the PEP 621 [project] table and Poetry's
// [tool.poetry] tables (via git-pkgs/manifests).
type PyprojectChecker struct {
	// Resolver resolves latest released versions. main.go wires up an
	// enrichment-backed resolver; tests inject a fake one.
	Resolver resolver.Resolver
}

func (PyprojectChecker) Filename() string { return "pyproject.toml" }

// LockfileNames lists the lockfiles the pyproject.toml-based tools produce.
func (PyprojectChecker) LockfileNames() []string {
	return []string{"poetry.lock", "uv.lock", "pdm.lock"}
}

func (c PyprojectChecker) Check(before, after string, hasLockfile bool) ([]mismatch.Mismatch, error) {
	return CheckPyproject(before, after, c.Resolver, hasLockfile)
}

// CheckPyproject compares pyproject.toml content before and after a Write
// and reports outdated exact pins, ranges that exclude the latest release
// (recommending a replacement range that includes it), and ranges with no
// lockfile alongside pyproject.toml. Dependencies the write didn't touch
// are left alone.
func CheckPyproject(before, after string, res resolver.Resolver, hasLockfile bool) ([]mismatch.Mismatch, error) {
	beforePins, err := parsePypi("pyproject.toml", before)
	if err != nil {
		return nil, err
	}
	afterPins, err := parsePypi("pyproject.toml", after)
	if err != nil {
		return nil, err
	}
	return pins.Diff(context.Background(), beforePins, afterPins, scheme, res, hasLockfile, formatRangeFix)
}
