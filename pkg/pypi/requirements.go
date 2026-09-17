package pypi

import (
	"context"

	"github.com/chains-project/yul/pkg/util/mismatch"
	"github.com/chains-project/yul/pkg/util/pins"
	"github.com/chains-project/yul/pkg/util/resolver"
)

// RequirementsChecker implements manifestchecker.ManifestChecker for
// requirements.txt.
type RequirementsChecker struct {
	// Resolver resolves latest released versions. main.go wires up an
	// enrichment-backed resolver; tests inject a fake one.
	Resolver resolver.Resolver
}

func (RequirementsChecker) Filename() string { return "requirements.txt" }

func (c RequirementsChecker) Check(before, after string) ([]mismatch.Mismatch, error) {
	return CheckRequirements(before, after, c.Resolver)
}

// CheckRequirements compares requirements.txt content before and after a
// Write and reports outdated exact pins plus ranges that exclude the
// latest release, recommending a hard "==" pin for each. Packages the
// write didn't touch are left alone.
func CheckRequirements(before, after string, res resolver.Resolver) ([]mismatch.Mismatch, error) {
	beforePins, err := parsePypiPins("requirements.txt", before)
	if err != nil {
		return nil, err
	}
	afterPins, err := parsePypiPins("requirements.txt", after)
	if err != nil {
		return nil, err
	}
	mismatches, err := pins.Diff(context.Background(), beforePins, afterPins, scheme, res)
	if err != nil {
		return nil, err
	}

	beforeRanges, err := parsePypiRanges("requirements.txt", before)
	if err != nil {
		return nil, err
	}
	afterRanges, err := parsePypiRanges("requirements.txt", after)
	if err != nil {
		return nil, err
	}
	rangeMismatches, err := pins.DiffRanges(context.Background(), beforeRanges, afterRanges, scheme, res, formatExactPin)
	if err != nil {
		return nil, err
	}

	return append(mismatches, rangeMismatches...), nil
}
