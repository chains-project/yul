// Package inspect deeply pretty-prints arbitrary Go values for debugging.
package inspect

import (
	"io"

	"github.com/davecgh/go-spew/spew"
)

// config is tuned for inspection: deterministic map ordering, pointer
// addresses shown, and circular references detected rather than looped.
var config = spew.ConfigState{
	Indent:                  "  ",
	SortKeys:                true,
	DisablePointerAddresses: false,
	DisableCapacities:       false,
	ContinueOnMethod:        true,
	SpewKeys:                true,
}

// Sdump returns a deep, human-readable dump of all values.
func Sdump(values ...any) string { return config.Sdump(values...) }

// Fdump writes a deep dump of all values to w.
func Fdump(w io.Writer, values ...any) { config.Fdump(w, values...) }

// Dump writes a deep dump of all values to stdout.
func Dump(values ...any) { config.Dump(values...) }
