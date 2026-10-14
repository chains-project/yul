// Package inspect provides deep pretty-printing of arbitrary Go values for
// debugging. It wraps github.com/davecgh/go-spew with debugging-friendly
// defaults: pointers are followed, cycles are detected, and map keys are
// sorted so output is stable across runs.
package inspect

import (
	"io"

	"github.com/davecgh/go-spew/spew"
)

// Config is the default configuration used by Dump, Sdump and Fdump.
var Config = &spew.ConfigState{
	Indent:                  "  ",
	SortKeys:                true, // deterministic map output
	DisablePointerAddresses: false,
	DisableCapacities:       false,
	ContinueOnMethod:        true, // show internals even if Stringer/error is implemented
	MaxDepth:                0,    // 0 = unlimited
}

// Dump writes a deep, annotated representation of each value to stdout.
func Dump(values ...any) { Config.Dump(values...) }

// Sdump returns a deep, annotated representation of each value as a string.
func Sdump(values ...any) string { return Config.Sdump(values...) }

// Fdump writes a deep, annotated representation of each value to w.
func Fdump(w io.Writer, values ...any) { Config.Fdump(w, values...) }
