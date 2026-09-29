// Package pprint renders arbitrary Go values in a deep, human-readable form
// intended for interactive debugging and inspection.
//
// It improves on fmt's %v/%#v verbs in the cases that matter most while
// debugging:
//
//   - pointers and interfaces are followed and expanded recursively;
//   - unexported struct fields are included, not hidden;
//   - reference cycles terminate instead of recursing forever;
//   - shared values are visible through their pointer addresses;
//   - output is indented with sorted map keys, so it diffs cleanly.
//
// Printing never invokes user-defined String or Format methods, so arbitrary
// values can be dumped without triggering side effects.
package pprint

import (
	"io"
	"os"

	"github.com/davecgh/go-spew/spew"
)

// Default is the configuration used by the package-level helpers. It is tuned
// for inspection rather than compact output.
var Default = &Printer{
	state: &spew.ConfigState{
		Indent:                  "    ",
		MaxDepth:                0,
		DisableMethods:          true,
		DisablePointerMethods:   true,
		DisablePointerAddresses: false,
		DisableCapacities:       false,
		ContinueOnMethod:        false,
		SortKeys:                true,
		SpewKeys:                true,
	},
}

// Printer renders values using a specific configuration.
type Printer struct {
	state *spew.ConfigState
}

// New returns a Printer that indents the output with the given unit. An empty
// indent falls back to the Default indentation.
func New(indent string) *Printer {
	c := *Default.state
	if indent != "" {
		c.Indent = indent
	}
	return &Printer{state: &c}
}

// Sdump returns the deep representation of the supplied values as a string.
func (p *Printer) Sdump(values ...interface{}) string {
	return p.state.Sdump(values...)
}

// Fdump writes the deep representation of values to w.
func (p *Printer) Fdump(w io.Writer, values ...interface{}) {
	p.state.Fdump(w, values...)
}

// Dump writes the deep representation of values to standard error.
func (p *Printer) Dump(values ...interface{}) {
	p.state.Fdump(os.Stderr, values...)
}

// Sdump returns the deep representation of values using Default.
func Sdump(values ...interface{}) string { return Default.Sdump(values...) }

// Fdump writes the deep representation of values to w using Default.
func Fdump(w io.Writer, values ...interface{}) { Default.Fdump(w, values...) }

// Dump writes the deep representation of values to standard error using Default.
func Dump(values ...interface{}) { Default.Dump(values...) }
