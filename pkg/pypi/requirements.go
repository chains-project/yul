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
	beforePins, err := parsePypi("requirements.txt", before)
	if err != nil {
		return nil, err
	}
	afterPins, err := parsePypi("requirements.txt", after)
	if err != nil {
		return nil, err
	}
	return pins.Diff(context.Background(), beforePins, afterPins, scheme, res, formatExactPin)
}
