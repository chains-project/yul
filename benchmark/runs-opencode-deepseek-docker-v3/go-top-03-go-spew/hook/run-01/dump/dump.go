package dump

import (
	"io"
	"os"

	"github.com/davecgh/go-spew/spew"
)

type Config struct {
	Indent                  string
	MaxDepth                int
	DisableMethods          bool
	DisablePointerMethods   bool
	DisablePointerAddresses bool
	DisableCapacities       bool
	ContinueOnMethod        bool
	SortKeys                bool
}

var Default = Config{
	Indent:                  "  ",
	MaxDepth:                0,
	DisablePointerAddresses: true,
	SortKeys:                true,
}

func (c Config) state() *spew.ConfigState {
	return &spew.ConfigState{
		Indent:                  c.Indent,
		MaxDepth:                c.MaxDepth,
		DisableMethods:          c.DisableMethods,
		DisablePointerMethods:   c.DisablePointerMethods,
		DisablePointerAddresses: c.DisablePointerAddresses,
		DisableCapacities:       c.DisableCapacities,
		ContinueOnMethod:        c.ContinueOnMethod,
		SortKeys:                c.SortKeys,
	}
}

func (c Config) Sdump(v ...any) string {
	return c.state().Sdump(v...)
}

func (c Config) Fdump(w io.Writer, v ...any) {
	c.state().Fdump(w, v...)
}

func Depth(n int) Config {
	c := Default
	c.MaxDepth = n
	return c
}

func Sdump(v ...any) string {
	return Default.Sdump(v...)
}

func Dump(v ...any) {
	Default.Fdump(os.Stdout, v...)
}

func Fdump(w io.Writer, v ...any) {
	Default.Fdump(w, v...)
}
