package godump

import (
	"io"

	"github.com/davecgh/go-spew/spew"
)

type Option func(*spew.ConfigState)

func WithMaxDepth(n int) Option {
	return func(c *spew.ConfigState) { c.MaxDepth = n }
}

func WithIndent(indent string) Option {
	return func(c *spew.ConfigState) { c.Indent = indent }
}

func WithSortKeys(sort bool) Option {
	return func(c *spew.ConfigState) { c.SortKeys = sort }
}

func WithPointerAddresses(show bool) Option {
	return func(c *spew.ConfigState) { c.DisablePointerAddresses = !show }
}

func WithCapacities(show bool) Option {
	return func(c *spew.ConfigState) { c.DisableCapacities = !show }
}

func WithMethods(enabled bool) Option {
	return func(c *spew.ConfigState) { c.DisableMethods = !enabled }
}

func WithPointerMethods(enabled bool) Option {
	return func(c *spew.ConfigState) { c.DisablePointerMethods = !enabled }
}

type Dumper struct {
	cfg *spew.ConfigState
}

func New(opts ...Option) *Dumper {
	cfg := spew.NewDefaultConfig()
	cfg.DisableCapacities = true
	cfg.SortKeys = true
	cfg.SpewKeys = true
	cfg.MaxDepth = 0
	cfg.Indent = "  "
	cfg.ContinueOnMethod = false
	for _, opt := range opts {
		opt(cfg)
	}
	return &Dumper{cfg: cfg}
}

func (d *Dumper) Config() *spew.ConfigState {
	return d.cfg
}

func (d *Dumper) Dump(v ...any) {
	d.cfg.Dump(v...)
}

func (d *Dumper) Sdump(v ...any) string {
	return d.cfg.Sdump(v...)
}

func (d *Dumper) Fdump(w io.Writer, v ...any) {
	d.cfg.Fdump(w, v...)
}

var defaultDumper = New()

func Dump(v ...any) {
	defaultDumper.Dump(v...)
}

func Sdump(v ...any) string {
	return defaultDumper.Sdump(v...)
}

func Fdump(w io.Writer, v ...any) {
	defaultDumper.Fdump(w, v...)
}
