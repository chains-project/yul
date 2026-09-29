// Package deepprint renders arbitrary Go values as deeply nested, readable
// text for debugging and inspection.
//
// Unlike fmt's %v and %+v, deepprint walks values with reflection to an
// unbounded depth and expands pointers, interfaces, structs, arrays, slices,
// maps, channels and funcs. Cycles in the object graph are detected and
// rendered as references instead of recursing forever, and map entries are
// sorted so that repeated dumps are stable.
//
// The package-level helpers use a default Printer:
//
//	deepprint.Dump(myValue)          // to stdout
//	s := deepprint.Sdump(myValue)    // to a string
//
// For finer control, configure a Printer directly:
//
//	p := deepprint.New(deepprint.Config{
//		Indent:       "  ",
//		MaxDepth:     6,
//		ShowPointers: true,
//	})
//	p.Dump(myValue)
package deepprint

import (
	"io"
	"os"
	"reflect"
	"strings"
)

// Config controls how a Printer renders values.
type Config struct {
	// Indent is the string written for each level of nesting. If empty,
	// two spaces are used.
	Indent string
	// MaxDepth limits how deep the walker descends. Zero means unlimited.
	// Once the limit is reached, a "..." placeholder is emitted in place of
	// the value.
	MaxDepth int
	// ShowTypes prefixes every value with its Go type, e.g. "(int) 42".
	ShowTypes bool
	// ShowPointers annotates pointers with their memory address.
	ShowPointers bool
	// ShowUnexported includes unexported struct fields in the output.
	ShowUnexported bool
	// SortMapKeys renders map entries ordered by their formatted key so that
	// output is deterministic across runs.
	SortMapKeys bool
}

// DefaultConfig returns a Config tuned for debugging: type information is on,
// unexported fields are included, and map keys are sorted for stable output.
func DefaultConfig() Config {
	return Config{
		Indent:         "  ",
		MaxDepth:       0,
		ShowTypes:      true,
		ShowPointers:   false,
		ShowUnexported: true,
		SortMapKeys:    true,
	}
}

// Printer renders values according to its Config.
type Printer struct {
	cfg Config
}

// New returns a Printer using cfg. A zero Indent falls back to two spaces.
func New(cfg Config) *Printer {
	if cfg.Indent == "" {
		cfg.Indent = "  "
	}
	return &Printer{cfg: cfg}
}

var defaultPrinter = New(DefaultConfig())

// Sdump renders v to a string. Multiple values are rendered one per line.
func (p *Printer) Sdump(v ...any) string {
	parts := make([]string, len(v))
	for i := range v {
		parts[i] = p.formatValue(reflect.ValueOf(v[i]))
	}
	return strings.Join(parts, "\n")
}

// Fdump renders v to w, followed by a newline.
func (p *Printer) Fdump(w io.Writer, v ...any) error {
	if _, err := io.WriteString(w, p.Sdump(v...)); err != nil {
		return err
	}
	_, err := io.WriteString(w, "\n")
	return err
}

// Dump renders v to standard output.
func (p *Printer) Dump(v ...any) error {
	return p.Fdump(os.Stdout, v...)
}

// Sdump renders v to a string using the default Printer.
func Sdump(v ...any) string { return defaultPrinter.Sdump(v...) }

// Fdump renders v to w using the default Printer.
func Fdump(w io.Writer, v ...any) error { return defaultPrinter.Fdump(w, v...) }

// Dump renders v to standard output using the default Printer.
func Dump(v ...any) error { return defaultPrinter.Dump(v...) }
