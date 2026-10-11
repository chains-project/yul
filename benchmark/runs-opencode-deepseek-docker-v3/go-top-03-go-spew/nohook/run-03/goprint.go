// Package goprint provides deep, cycle-safe pretty-printing of arbitrary Go
// values for debugging and inspection.
//
// Unlike fmt's %v verb, goprint recurses into struct fields (including
// unexported ones), reports the types of composite values, detects reference
// cycles, sorts map keys for deterministic output, and can bound both the
// recursion depth and the number of elements it emits. A value that cannot be
// inspected never panics the program: the error is reported in the output.
package goprint

import (
	"bytes"
	"fmt"
	"io"
	"os"
	"reflect"
	"sort"
	"strconv"
	"strings"
)

// Options configures printing. The zero value is usable and prints with tab
// indentation and no depth or item limits.
type Options struct {
	// Indent is the string written once per nesting level. Defaults to "\t".
	Indent string
	// MaxDepth limits how deep the printer recurses. A value <= 0 means no
	// limit. Values beyond the limit are rendered as "...".
	MaxDepth int
	// MaxItems limits how many elements of a slice, array or map are printed.
	// A value <= 0 means no limit.
	MaxItems int
}

func (o Options) indent() string {
	if o.Indent == "" {
		return "\t"
	}
	return o.Indent
}

// Sprint returns a deep, pretty-printed representation of v.
func Sprint(v any) string {
	return SprintOpts(v, Options{})
}

// SprintOpts is Sprint with explicit options.
func SprintOpts(v any, opts Options) string {
	var buf bytes.Buffer
	FprintOpts(&buf, v, opts)
	return buf.String()
}

// Fprint writes the deep representation of v to w.
func Fprint(w io.Writer, v any) error {
	return FprintOpts(w, v, Options{})
}

// FprintOpts writes the deep representation of v to w using opts.
func FprintOpts(w io.Writer, v any, opts Options) (err error) {
	p := &printer{opts: opts, visited: map[visit]bool{}, buf: &bytes.Buffer{}}
	defer func() {
		if r := recover(); r != nil {
			err = fmt.Errorf("goprint: recovered while printing %T: %v", v, r)
		}
	}()
	p.value(reflect.ValueOf(v), 0)
	_, err = io.WriteString(w, p.buf.String())
	return err
}

// Print writes the deep representation of each value to standard output,
// one per line.
func Print(v ...any) {
	for _, x := range v {
		os.Stdout.WriteString(Sprint(x))
		os.Stdout.WriteString("\n")
	}
}

// visit identifies a reference value on the current printing path. It is used
// to detect cycles without treating shared but acyclic values as cycles.
type visit struct {
	ptr uintptr
	typ reflect.Type
}

type printer struct {
	opts    Options
	visited map[visit]bool
	buf     *bytes.Buffer
	compact bool
}

func (p *printer) write(s string) { p.buf.WriteString(s) }

// writeIndent starts a new (indented) line. It is a no-op in compact mode.
func (p *printer) writeIndent(depth int) {
	if p.compact {
		return
	}
	p.write("\n")
	p.write(strings.Repeat(p.opts.indent(), depth))
}

// withCycle guards a reference value. If fn is invoked while v is already on
// the active path, a cycle marker is printed instead.
func (p *printer) withCycle(v reflect.Value, fn func()) {
	key := visit{ptr: v.Pointer(), typ: v.Type()}
	if p.visited[key] {
		p.write("<cycle>")
		return
	}
	p.visited[key] = true
	defer delete(p.visited, key)
	fn()
}

// inline renders v on a single line, sharing the cycle-detection state.
func (p *printer) inline(v reflect.Value, depth int) string {
	sub := &printer{opts: p.opts, visited: p.visited, buf: &bytes.Buffer{}, compact: true}
	sub.value(v, depth)
	return sub.buf.String()
}

// limit returns how many elements of a sequence of length n should be printed.
func (p *printer) limit(n int) int {
	if p.opts.MaxItems > 0 && n > p.opts.MaxItems {
		return p.opts.MaxItems
	}
	return n
}

func (p *printer) value(v reflect.Value, depth int) {
	if !v.IsValid() {
		p.write("<nil>")
		return
	}

	if v.Kind() == reflect.Interface {
		if v.IsNil() {
			p.write("nil")
			return
		}
		p.value(v.Elem(), depth)
		return
	}

	if p.opts.MaxDepth > 0 && depth > p.opts.MaxDepth && isComposite(v.Kind()) {
		p.write("...")
		return
	}

	switch v.Kind() {
	case reflect.Bool:
		p.write(strconv.FormatBool(v.Bool()))
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		p.write(strconv.FormatInt(v.Int(), 10))
	case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64, reflect.Uintptr:
		p.write(strconv.FormatUint(v.Uint(), 10))
	case reflect.Float32:
		p.write(strconv.FormatFloat(v.Float(), 'g', -1, 32))
	case reflect.Float64:
		p.write(strconv.FormatFloat(v.Float(), 'g', -1, 64))
	case reflect.Complex64:
		p.write(formatComplex(v.Complex(), 32))
	case reflect.Complex128:
		p.write(formatComplex(v.Complex(), 64))
	case reflect.String:
		p.write(strconv.Quote(v.String()))
	case reflect.Ptr:
		p.pointer(v, depth)
	case reflect.Struct:
		p.structValue(v, depth)
	case reflect.Map:
		p.mapValue(v, depth)
	case reflect.Slice:
		p.sliceValue(v, depth)
	case reflect.Array:
		p.sequence(v, depth, v.Type().String())
	case reflect.Chan:
		p.write("(" + v.Type().String() + ")(" + hexPtr(v.Pointer()) + ")")
	case reflect.Func:
		if v.IsNil() {
			p.write("(" + v.Type().String() + ")(nil)")
		} else {
			p.write("(" + v.Type().String() + ")(" + hexPtr(v.Pointer()) + ")")
		}
	case reflect.UnsafePointer:
		p.write("unsafe.Pointer(" + hexPtr(v.Pointer()) + ")")
	default:
		p.write(fmt.Sprintf("<%s>", v.Type()))
	}
}

func isComposite(k reflect.Kind) bool {
	switch k {
	case reflect.Ptr, reflect.Struct, reflect.Map, reflect.Slice, reflect.Array:
		return true
	default:
		return false
	}
}

func (p *printer) pointer(v reflect.Value, depth int) {
	if v.IsNil() {
		p.write("(" + v.Type().String() + ")(nil)")
		return
	}
	p.withCycle(v, func() {
		p.write("&")
		p.value(v.Elem(), depth)
	})
}

func (p *printer) structValue(v reflect.Value, depth int) {
	t := v.Type()
	p.write(t.String())
	p.write("{")
	for i := 0; i < t.NumField(); i++ {
		if i > 0 {
			p.write(",")
		}
		if p.compact {
			p.write(" ")
		} else {
			p.writeIndent(depth + 1)
		}
		p.write(t.Field(i).Name)
		p.write(": ")
		p.value(v.Field(i), depth+1)
	}
	if t.NumField() > 0 {
		if p.compact {
			p.write(" ")
		} else {
			p.writeIndent(depth)
		}
	}
	p.write("}")
}

func (p *printer) mapValue(v reflect.Value, depth int) {
	if v.IsNil() {
		p.write(v.Type().String() + "(nil)")
		return
	}
	p.withCycle(v, func() {
		n := v.Len()
		p.write(v.Type().String())
		if n == 0 {
			p.write("{}")
			return
		}

		type entry struct {
			key  reflect.Value
			text string
		}
		keys := v.MapKeys()
		entries := make([]entry, len(keys))
		for i, k := range keys {
			entries[i] = entry{key: k, text: p.inline(k, depth+1)}
		}
		sort.Slice(entries, func(i, j int) bool { return entries[i].text < entries[j].text })

		limit := p.limit(n)
		p.write("{")
		for i := 0; i < limit; i++ {
			if i > 0 {
				p.write(",")
			}
			if p.compact {
				p.write(" ")
			} else {
				p.writeIndent(depth + 1)
			}
			p.write(entries[i].text)
			p.write(": ")
			p.value(v.MapIndex(entries[i].key), depth+1)
		}
		if limit < n {
			p.write(",")
			if p.compact {
				p.write(" ")
			} else {
				p.writeIndent(depth + 1)
			}
			p.write(fmt.Sprintf("... (%d more)", n-limit))
		}
		if p.compact {
			p.write(" ")
		} else {
			p.writeIndent(depth)
		}
		p.write("}")
	})
}

func (p *printer) sliceValue(v reflect.Value, depth int) {
	if v.IsNil() {
		p.write(v.Type().String() + "(nil)")
		return
	}
	p.withCycle(v, func() {
		// Copy the header to avoid a liveness issue: taking the address of a
		// slice's backing array keeps it alive for the duration of the print.
		p.sequence(v, depth, v.Type().String())
	})
}

func (p *printer) sequence(v reflect.Value, depth int, typeStr string) {
	n := v.Len()
	p.write(typeStr)
	if n == 0 {
		p.write("{}")
		return
	}
	limit := p.limit(n)
	p.write("{")
	for i := 0; i < limit; i++ {
		if i > 0 {
			p.write(",")
		}
		if p.compact {
			p.write(" ")
		} else {
			p.writeIndent(depth + 1)
		}
		p.value(v.Index(i), depth+1)
	}
	if limit < n {
		p.write(",")
		if p.compact {
			p.write(" ")
		} else {
			p.writeIndent(depth + 1)
		}
		p.write(fmt.Sprintf("... (%d more)", n-limit))
	}
	if p.compact {
		p.write(" ")
	} else {
		p.writeIndent(depth)
	}
	p.write("}")
}

func formatComplex(c complex128, bits int) string {
	re := strconv.FormatFloat(real(c), 'g', -1, bits)
	im := strconv.FormatFloat(imag(c), 'g', -1, bits)
	if !strings.HasPrefix(im, "-") {
		im = "+" + im
	}
	return "(" + re + im + "i)"
}

func hexPtr(p uintptr) string {
	return "0x" + strconv.FormatUint(uint64(p), 16)
}
