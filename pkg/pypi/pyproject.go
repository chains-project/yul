package pypi

import (
	"fmt"
	"strings"

	"github.com/chains-project/yul/pkg/util/mismatch"
	"github.com/pelletier/go-toml/v2"
)

// PyprojectChecker implements manifestchecker.ManifestChecker for
// pyproject.toml, covering the PEP 621 standard [project] table. It does
// not understand tool-specific dependency tables (e.g. Poetry's
// [tool.poetry.dependencies]), which use their own version syntax.
type PyprojectChecker struct{}

func (PyprojectChecker) Filename() string { return "pyproject.toml" }

func (PyprojectChecker) Check(before, after string) ([]mismatch.Mismatch, error) {
	return CheckPyproject(before, after)
}

type pyprojectDoc struct {
	Project struct {
		Dependencies         []string            `toml:"dependencies"`
		OptionalDependencies map[string][]string `toml:"optional-dependencies"`
	} `toml:"project"`
}

func parsePyproject(content string) (map[string]string, error) {
	pins := make(map[string]string)
	if strings.TrimSpace(content) == "" {
		return pins, nil
	}

	var doc pyprojectDoc
	if err := toml.Unmarshal([]byte(content), &doc); err != nil {
		return nil, fmt.Errorf("parsing pyproject.toml: %w", err)
	}

	addAll := func(reqs []string) {
		for _, req := range reqs {
			if name, version, ok := parseRequirementLine(req); ok {
				pins[name] = version
			}
		}
	}
	addAll(doc.Project.Dependencies)
	for _, reqs := range doc.Project.OptionalDependencies {
		addAll(reqs)
	}

	return pins, nil
}

// CheckPyproject compares pyproject.toml content before and after a Write
// and reports any exactly-pinned ("==") dependency in [project.dependencies]
// or [project.optional-dependencies] that is newly added or whose pinned
// version was just changed, and is older than the latest release on PyPI.
func CheckPyproject(before, after string) ([]mismatch.Mismatch, error) {
	beforePins, err := parsePyproject(before)
	if err != nil {
		return nil, err
	}
	afterPins, err := parsePyproject(after)
	if err != nil {
		return nil, err
	}
	return diffPins(beforePins, afterPins)
}
