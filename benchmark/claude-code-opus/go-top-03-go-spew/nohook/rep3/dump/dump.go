// Package dump deeply pretty-prints arbitrary Go values for inspection.
package dump

import (
	"io"

	"github.com/davecgh/go-spew/spew"
)

// config is tuned for debugging: sorted map keys for stable output,
// pointer addresses hidden so diffs between runs stay readable, and
// Stringer/error methods bypassed so the raw structure is always shown.
var config = spew.ConfigState{
	Indent:                  "  ",
	SortKeys:                true,
	DisablePointerAddresses: true,
	DisableMethods:          true,
	SpewKeys:                true,
}

// Sdump returns a deep, human-readable representation of the values.
func Sdump(values ...any) string { return config.Sdump(values...) }

// Fdump writes a deep, human-readable representation of the values to w.
func Fdump(w io.Writer, values ...any) { config.Fdump(w, values...) }
