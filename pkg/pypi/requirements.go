package pypi

import (
	"strings"

	"github.com/chains-project/yul/pkg/util/mismatch"
)

// RequirementsChecker implements manifestchecker.ManifestChecker for
// requirements.txt.
type RequirementsChecker struct{}

func (RequirementsChecker) Filename() string { return "requirements.txt" }

func (RequirementsChecker) Check(before, after string) ([]mismatch.Mismatch, error) {
	return CheckRequirements(before, after)
}

func parseRequirements(content string) map[string]string {
	pins := make(map[string]string)
	for _, line := range strings.Split(content, "\n") {
		if name, version, ok := parseRequirementLine(line); ok {
			pins[name] = version
		}
	}
	return pins
}

// CheckRequirements compares requirements.txt content before and after a
// Write and reports any exactly-pinned ("==") package that is newly added
// or whose pinned version was just changed, and is older than the latest
// release on PyPI. Packages the write didn't touch, or that aren't pinned
// exactly, are left alone.
func CheckRequirements(before, after string) ([]mismatch.Mismatch, error) {
	return diffPins(parseRequirements(before), parseRequirements(after))
}
