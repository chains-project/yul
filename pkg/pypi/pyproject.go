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

func (c PyprojectChecker) Check(before, after string) ([]mismatch.Mismatch, error) {
	return CheckPyproject(before, after, c.Resolver)
}

// CheckPyproject compares pyproject.toml content before and after a Write
// and reports any exactly-pinned ("==") dependency that is newly added or
// whose pinned version was just changed, and doesn't match the latest
// release res knows about. Packages the write didn't touch, or that aren't
// pinned exactly, are left alone.
func CheckPyproject(before, after string, res resolver.Resolver) ([]mismatch.Mismatch, error) {
	beforePins, err := parsePypiPins("pyproject.toml", before)
	if err != nil {
		return nil, err
	}
	afterPins, err := parsePypiPins("pyproject.toml", after)
	if err != nil {
		return nil, err
	}
	return pins.Diff(context.Background(), beforePins, afterPins, scheme, res)
}
