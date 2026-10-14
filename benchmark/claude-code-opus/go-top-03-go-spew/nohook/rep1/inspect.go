// Package inspect deeply pretty-prints arbitrary Go values for debugging.
//
// It wraps github.com/davecgh/go-spew with defaults tuned for inspection:
// nested pointers are followed, unexported fields are shown, cycles are
// detected, and map keys are sorted so output is stable across runs.
package inspect

import (
	"io"
	"os"

	"github.com/davecgh/go-spew/spew"
)

// Config controls how values are rendered.
type Config = spew.ConfigState

// Default is the configuration used by the package-level helpers.
var Default = &Config{
	Indent:                  "  ",
	SortKeys:                true, // deterministic map output
	DisablePointerAddresses: true, // stable output across runs
	DisableCapacities:       true,
	ContinueOnMethod:        true, // show Stringer/error output *and* the underlying fields
	MaxDepth:                0,    // unlimited
}

// Sdump returns a deep, human-readable representation of the values.
func Sdump(values ...any) string { return Default.Sdump(values...) }

// Fdump writes a deep representation of the values to w.
func Fdump(w io.Writer, values ...any) { Default.Fdump(w, values...) }

// Dump writes a deep representation of the values to stderr, keeping
// debugging output out of a program's stdout.
func Dump(values ...any) { Default.Fdump(os.Stderr, values...) }
