package main

import (
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"

	"github.com/chains-project/yul/pkg/maven"
	"github.com/chains-project/yul/pkg/util/manifestchecker"
)

// checkers is the registry of manifest checkers the hook dispatches to,
// keyed off which manifest filename each one owns. Add an entry here as
// each ecosystem's checker is implemented.
var checkers = []manifestchecker.ManifestChecker{
	maven.Checker{},
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
		FilePath string `json:"file_path"`
		Content  string `json:"content"`
	} `json:"tool_input"`
}

// runHook is a PreToolUse hook for the Write tool. It figures out which
// ecosystem owns the manifest being written (by filename), and blocks
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

	if in.ToolName != "Write" {
		os.Exit(0)
	}

	checker := checkerFor(filepath.Base(in.ToolInput.FilePath))
	if checker == nil {
		os.Exit(0) // not a manifest we know how to check
	}

	before, err := os.ReadFile(in.ToolInput.FilePath)
	if err != nil {
		before = nil // file doesn't exist yet: every dependency in it is new
	}

	mismatches, err := checker.Check(string(before), in.ToolInput.Content)
	if err != nil {
		fmt.Fprintf(os.Stderr, "hook: %v\n", err)
		os.Exit(0) // fail open: a resolver/network error shouldn't block the write
	}

	if len(mismatches) == 0 {
		os.Exit(0)
	}

	fmt.Fprintln(os.Stderr, "outdated dependencies, use these versions instead:")
	for _, m := range mismatches {
		fmt.Fprintf(os.Stderr, "  %s:%s  %s -> %s\n", m.Namespace, m.Name, m.Current, m.Latest)
	}
	os.Exit(2)
}

func main() {
	runHook()
}
