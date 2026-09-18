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

func (c RequirementsChecker) Check(before, after string, _ bool) ([]mismatch.Mismatch, error) {
	return CheckRequirements(before, after, c.Resolver)
}

// CheckRequirements compares requirements.txt content before and after a
// Write and reports outdated exact pins. Packages the write didn't touch
// are left alone.
//
// requirements.txt has no lockfile convention of its own (it's typically
// the compiled/pinned output already), so RequirementsChecker never
// implements manifestchecker.LockfileAware and pins.Diff is always told a
// lockfile is present here - regardless of what Check's own hasLockfile
// argument says - so a range is never flagged for a missing lockfile.
func CheckRequirements(before, after string, res resolver.Resolver) ([]mismatch.Mismatch, error) {
	beforePins, err := parsePypiPins("requirements.txt", before)
	if err != nil {
		return nil, err
	}
	afterPins, err := parsePypiPins("requirements.txt", after)
	if err != nil {
		return nil, err
	}
	return pins.Diff(context.Background(), beforePins, afterPins, scheme, res, pins.NoLockfileConvention)
}
