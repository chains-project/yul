// Package inspect deeply pretty-prints arbitrary Go values for debugging.
//
// It wraps github.com/davecgh/go-spew, which walks values via reflection,
// follows pointers, prints unexported fields, and detects cycles.
package inspect

import (
	"io"

	"github.com/davecgh/go-spew/spew"
)

// Config controls the dump output.
var Config = spew.ConfigState{
	Indent:                  "  ",
	SortKeys:                true, // deterministic map output
	DisablePointerAddresses: true, // stable output across runs
	DisableCapacities:       true,
	SpewKeys:                true,
}

// Sdump returns a deep, multi-line representation of the given values.
func Sdump(values ...any) string { return Config.Sdump(values...) }

// Dump writes a deep representation of the given values to stdout.
func Dump(values ...any) { Config.Dump(values...) }

// Fdump writes a deep representation of the given values to w.
func Fdump(w io.Writer, values ...any) { Config.Fdump(w, values...) }
