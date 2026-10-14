// Package inspect provides deep pretty-printing of arbitrary Go values for
// debugging. It wraps github.com/davecgh/go-spew with defaults suited to
// interactive inspection.
package inspect

import (
	"io"
	"os"

	"github.com/davecgh/go-spew/spew"
)

// Config is the default configuration used by the package-level helpers.
// Callers may copy and tweak it for custom behavior.
var Config = spew.ConfigState{
	Indent:                  "  ",
	SortKeys:                true, // deterministic map output
	DisablePointerAddresses: false,
	DisableCapacities:       true,
	DisableMethods:          true, // show raw fields rather than String()/Error()
	MaxDepth:                0,    // unlimited; cycles are detected automatically
}

// Dump writes a deep, typed representation of each value to stdout.
func Dump(vs ...any) { Config.Fdump(os.Stdout, vs...) }

// Fdump writes a deep, typed representation of each value to w.
func Fdump(w io.Writer, vs ...any) { Config.Fdump(w, vs...) }

// Sdump returns a deep, typed representation of each value as a string.
func Sdump(vs ...any) string { return Config.Sdump(vs...) }
