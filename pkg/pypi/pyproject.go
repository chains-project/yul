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
// and reports outdated exact pins plus ranges that exclude the latest
// release, recommending a hard "==" pin for each. Dependencies the write
// didn't touch are left alone.
func CheckPyproject(before, after string, res resolver.Resolver) ([]mismatch.Mismatch, error) {
	beforePins, err := parsePypiPins("pyproject.toml", before)
	if err != nil {
		return nil, err
	}
	afterPins, err := parsePypiPins("pyproject.toml", after)
	if err != nil {
		return nil, err
	}
	mismatches, err := pins.Diff(context.Background(), beforePins, afterPins, scheme, res)
	if err != nil {
		return nil, err
	}

	beforeRanges, err := parsePypiRanges("pyproject.toml", before)
	if err != nil {
		return nil, err
	}
	afterRanges, err := parsePypiRanges("pyproject.toml", after)
	if err != nil {
		return nil, err
	}
	rangeMismatches, err := pins.DiffRanges(context.Background(), beforeRanges, afterRanges, scheme, res, formatExactPin)
	if err != nil {
		return nil, err
	}

	return append(mismatches, rangeMismatches...), nil
}
