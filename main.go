package main

import (
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"

	"github.com/chains-project/yul/pkg/maven"
	"github.com/chains-project/yul/pkg/npm"
	"github.com/chains-project/yul/pkg/pypi"
	"github.com/chains-project/yul/pkg/util/manifestchecker"
)

// checkers is the registry of manifest checkers the hook dispatches to,
// keyed off which manifest filename each one owns. Add an entry here as
// each ecosystem's checker is implemented.
var checkers = []manifestchecker.ManifestChecker{
	maven.Checker{},
	pypi.RequirementsChecker{},
	pypi.PyprojectChecker{},
	npm.Checker{},
}

func checkerFor(filename string) manifestchecker.ManifestChecker {
	for _, c := range checkers {
		if c.Filename() == filename {
			return c
		}
	}
	return nil
}

// hookInput is the subset of Claude Code's PreToolUse hook payload we need.
type hookInput struct {
	ToolName  string `json:"tool_name"`
	ToolInput struct {
		FilePath   string `json:"file_path"`
		Content    string `json:"content"`     // Write
		OldString  string `json:"old_string"`  // Edit
		NewString  string `json:"new_string"`  // Edit
		ReplaceAll bool   `json:"replace_all"` // Edit
	} `json:"tool_input"`
}

// runHook is a PreToolUse hook for the Write and Edit tools. It figures out
// which ecosystem owns the manifest being written (by filename), and blocks
// (exit 2) if a newly added/changed dependency is pinned older than what's
// actually released. Claude sees the block reason on stderr and can retry.
func runHook() {
	raw, err := io.ReadAll(os.Stdin)
	if err != nil {
		fmt.Fprintf(os.Stderr, "hook: reading stdin: %v\n", err)
		os.Exit(0) // fail open: don't block Claude on a hook plumbing error
	}

	var in hookInput
	if err := json.Unmarshal(raw, &in); err != nil {
		fmt.Fprintf(os.Stderr, "hook: parsing hook payload: %v\n", err)
		os.Exit(0)
	}

	if in.ToolName != "Write" && in.ToolName != "Edit" {
		os.Exit(0)
	}

	checker := checkerFor(filepath.Base(in.ToolInput.FilePath))
	if checker == nil {
		os.Exit(0) // not a manifest we know how to check
	}

	rawBefore, err := os.ReadFile(in.ToolInput.FilePath)
	if err != nil {
		rawBefore = nil // file doesn't exist yet: every dependency in it is new
	}
	before := string(rawBefore)

	after := in.ToolInput.Content
	if in.ToolName == "Edit" {
		if !strings.Contains(before, in.ToolInput.OldString) {
			// Edit tool itself would fail on this; nothing for us to check.
			os.Exit(0)
		}
		count := 1
		if in.ToolInput.ReplaceAll {
			count = -1
		}
		after = strings.Replace(before, in.ToolInput.OldString, in.ToolInput.NewString, count)
	}

	mismatches, err := checker.Check(before, after)
	if err != nil {
		fmt.Fprintf(os.Stderr, "hook: %v\n", err)
		os.Exit(0) // fail open: a resolver/network error shouldn't block the write
	}

	if len(mismatches) == 0 {
		os.Exit(0)
	}

	fmt.Fprintln(os.Stderr, "outdated dependencies, use these versions instead:")
	for _, m := range mismatches {
		name := m.Name
		if m.Namespace != "" {
			name = m.Namespace + ":" + m.Name
		}
		fmt.Fprintf(os.Stderr, "  %s  %s -> %s\n", name, m.Current, m.Latest)
	}
	os.Exit(2)
}

func main() {
	runHook()
}
