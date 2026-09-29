package inspect

import (
	"io"

	"github.com/davecgh/go-spew/spew"
)

var Config = spew.ConfigState{
	Indent:                  "    ",
	SortKeys:                true,
	DisableMethods:          true,
	DisablePointerMethods:   true,
	DisablePointerAddresses: true,
	DisableCapacities:       true,
}

func Sdump(values ...any) string {
	if len(values) == 1 {
		return Config.Sdump(values[0])
	}
	return Config.Sdump(values)
}

func Dump(values ...any) {
	Config.Dump(values...)
}

func Fdump(w io.Writer, values ...any) {
	Config.Fdump(w, values...)
}
