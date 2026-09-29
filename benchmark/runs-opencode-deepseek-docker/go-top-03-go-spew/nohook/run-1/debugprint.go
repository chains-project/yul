// Package debugprint renders arbitrary Go values, including nested and
// cyclic data structures, as human-readable text for debugging and
// inspection.
package debugprint

import (
	"fmt"
	"io"
	"os"
	"reflect"
	"sort"
	"strconv"
	"strings"
)

// Printer pretty-prints Go values according to a Config.
type Printer struct {
	cfg *Config
}

// New returns a Printer using a copy of cfg. A nil cfg uses
// NewDefaultConfig.
func New(cfg *Config) *Printer {
	if cfg == nil {
		cfg = NewDefaultConfig()
	}
	c := *cfg
	if c.Indent == "" {
		c.Indent = "  "
	}
	return &Printer{cfg: &c}
}

// NewDefaultPrinter returns a Printer with the default configuration.
func NewDefaultPrinter() *Printer { return New(nil) }

// Sdump returns the pretty-printed form of the supplied values, one per
// line, requiring no imports beyond this package.
func (p *Printer) Sdump(a ...any) string {
	var b strings.Builder
	p.Fdump(&b, a...)
	return b.String()
}

// Dump writes the pretty-printed values to standard error.
func (p *Printer) Dump(a ...any) { p.Fdump(os.Stderr, a...) }

// Fdump writes the pretty-printed values to w.
func (p *Printer) Fdump(w io.Writer, a ...any) {
	s := &state{cfg: p.cfg, visited: make(map[uintptr]struct{})}
	for i, v := range a {
		if i > 0 {
			s.buf.WriteByte('\n')
		}
		s.dump(reflect.ValueOf(v), 0)
		s.buf.WriteByte('\n')
	}
	io.WriteString(w, s.buf.String())
}

// Sdump pretty-prints the values using the default configuration.
func Sdump(a ...any) string { return NewDefaultPrinter().Sdump(a...) }

// Dump pretty-prints the values to standard error using the default
// configuration.
func Dump(a ...any) { NewDefaultPrinter().Dump(a...) }

// Fdump pretty-prints the values to w using the default configuration.
func Fdump(w io.Writer, a ...any) { NewDefaultPrinter().Fdump(w, a...) }

type state struct {
	cfg     *Config
	buf     strings.Builder
	visited map[uintptr]struct{}
}

func (s *state) writeIndent(depth int) {
	for i := 0; i < depth; i++ {
		s.buf.WriteString(s.cfg.Indent)
	}
}

func (s *state) writeType(t reflect.Type) {
	if s.cfg.PrintType {
		s.buf.WriteString(typeName(t))
	}
}

func (s *state) dump(v reflect.Value, depth int) {
	if !v.IsValid() {
		s.buf.WriteString("<nil>")
		return
	}
	if s.cfg.MaxDepth > 0 && depth >= s.cfg.MaxDepth {
		s.buf.WriteString("...")
		return
	}

	switch v.Kind() {
	case reflect.Interface:
		if v.IsNil() {
			s.buf.WriteString("nil")
			return
		}
		elem := v.Elem()
		s.buf.WriteByte('(')
		s.buf.WriteString(typeName(elem.Type()))
		s.buf.WriteByte(')')
		s.dump(elem, depth)

	case reflect.Ptr:
		if v.IsNil() {
			s.buf.WriteByte('(')
			s.buf.WriteString(typeName(v.Type()))
			s.buf.WriteString(")(nil)")
			return
		}
		addr := v.Pointer()
		if s.seen(addr) {
			s.writeCycle(addr)
			return
		}
		s.enter(addr)
		defer s.leave(addr)
		s.buf.WriteByte('&')
		s.dump(v.Elem(), depth)

	case reflect.Struct:
		s.dumpStruct(v, depth)

	case reflect.Map:
		s.dumpMap(v, depth)

	case reflect.Slice:
		if v.IsNil() {
			s.buf.WriteByte('(')
			s.buf.WriteString(typeName(v.Type()))
			s.buf.WriteString(")(nil)")
			return
		}
		addr := v.Pointer()
		if s.seen(addr) {
			s.writeCycle(addr)
			return
		}
		s.enter(addr)
		defer s.leave(addr)
		s.dumpList(v, depth)

	case reflect.Array:
		s.dumpList(v, depth)

	case reflect.String:
		s.buf.WriteString(strconv.Quote(v.String()))

	case reflect.Bool:
		s.buf.WriteString(strconv.FormatBool(v.Bool()))

	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		s.buf.WriteString(strconv.FormatInt(v.Int(), 10))

	case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64, reflect.Uintptr:
		s.buf.WriteString(strconv.FormatUint(v.Uint(), 10))

	case reflect.Float32, reflect.Float64:
		s.buf.WriteString(strconv.FormatFloat(v.Float(), 'g', -1, v.Type().Bits()))

	case reflect.Complex64, reflect.Complex128:
		s.buf.WriteString(strconv.FormatComplex(v.Complex(), 'g', -1, v.Type().Bits()))

	case reflect.Chan, reflect.Func, reflect.UnsafePointer:
		s.buf.WriteByte('(')
		s.buf.WriteString(typeName(v.Type()))
		s.buf.WriteString(")(")
		if v.IsNil() {
			s.buf.WriteString("nil")
		} else {
			s.buf.WriteString(fmt.Sprintf("%#x", v.Pointer()))
		}
		s.buf.WriteByte(')')

	default:
		s.buf.WriteString("<")
		s.buf.WriteString(v.Kind().String())
		s.buf.WriteString(">")
	}
}

func (s *state) dumpStruct(v reflect.Value, depth int) {
	t := v.Type()
	s.writeType(t)
	s.buf.WriteByte('{')
	n := t.NumField()
	if n == 0 {
		s.buf.WriteByte('}')
		return
	}
	for i := 0; i < n; i++ {
		s.buf.WriteByte('\n')
		s.writeIndent(depth + 1)
		s.buf.WriteString(t.Field(i).Name)
		s.buf.WriteString(": ")
		s.dump(v.Field(i), depth+1)
		if i < n-1 {
			s.buf.WriteByte(',')
		}
	}
	s.buf.WriteByte('\n')
	s.writeIndent(depth)
	s.buf.WriteByte('}')
}

func (s *state) dumpMap(v reflect.Value, depth int) {
	if v.IsNil() {
		s.buf.WriteByte('(')
		s.buf.WriteString(typeName(v.Type()))
		s.buf.WriteString(")(nil)")
		return
	}
	addr := v.Pointer()
	if s.seen(addr) {
		s.writeCycle(addr)
		return
	}
	s.enter(addr)
	defer s.leave(addr)

	s.writeType(v.Type())
	s.buf.WriteByte('{')
	keys := v.MapKeys()
	if s.cfg.SortMapKeys {
		sort.Slice(keys, func(i, j int) bool {
			return fmt.Sprintf("%#v", keys[i]) < fmt.Sprintf("%#v", keys[j])
		})
	}
	if len(keys) == 0 {
		s.buf.WriteByte('}')
		return
	}
	for i, k := range keys {
		s.buf.WriteByte('\n')
		s.writeIndent(depth + 1)
		s.dump(k, depth+1)
		s.buf.WriteString(": ")
		s.dump(v.MapIndex(k), depth+1)
		if i < len(keys)-1 {
			s.buf.WriteByte(',')
		}
	}
	s.buf.WriteByte('\n')
	s.writeIndent(depth)
	s.buf.WriteByte('}')
}

func (s *state) dumpList(v reflect.Value, depth int) {
	s.writeType(v.Type())
	s.buf.WriteByte('[')
	n := v.Len()
	if n == 0 {
		s.buf.WriteByte(']')
		return
	}
	for i := 0; i < n; i++ {
		s.buf.WriteByte('\n')
		s.writeIndent(depth + 1)
		s.dump(v.Index(i), depth+1)
		if i < n-1 {
			s.buf.WriteByte(',')
		}
	}
	s.buf.WriteByte('\n')
	s.writeIndent(depth)
	s.buf.WriteByte(']')
}

func (s *state) seen(addr uintptr) bool {
	_, ok := s.visited[addr]
	return ok
}

func (s *state) enter(addr uintptr) { s.visited[addr] = struct{}{} }
func (s *state) leave(addr uintptr) { delete(s.visited, addr) }

func (s *state) writeCycle(addr uintptr) {
	s.buf.WriteString("<cycle to ")
	s.buf.WriteString(fmt.Sprintf("%#x", addr))
	s.buf.WriteByte('>')
}

func typeName(t reflect.Type) string {
	if t == nil {
		return "<nil>"
	}
	return t.String()
}
