// Package debugprint provides a reflection-based pretty-printer for
// inspecting arbitrary Go values.
//
// Unlike fmt's %#v verb, it expands nested values across multiple indented
// lines and detects reference cycles so recursive data structures terminate
// instead of overflowing the stack. Map keys are sorted so output is stable
// between runs.
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

const indentUnit = "  "

// visit identifies a reference value on the current traversal path. It is used
// to break cycles.
type visit struct {
	typ reflect.Type
	ptr uintptr
}

type printer struct {
	sb   strings.Builder
	seen map[visit]bool
}

// Sprint returns a deeply indented representation of the supplied values,
// separated by a single space when more than one is given.
func Sprint(vals ...interface{}) string {
	p := printer{seen: make(map[visit]bool)}
	for i, v := range vals {
		if i > 0 {
			p.sb.WriteByte(' ')
		}
		p.write(reflect.ValueOf(v), 0)
	}
	return p.sb.String()
}

// Sprintln is like Sprint but appends a newline.
func Sprintln(vals ...interface{}) string {
	return Sprint(vals...) + "\n"
}

// Fprint writes the representation of vals to w.
func Fprint(w io.Writer, vals ...interface{}) (int, error) {
	return io.WriteString(w, Sprint(vals...))
}

// Fprintln writes the representation of vals to w followed by a newline.
func Fprintln(w io.Writer, vals ...interface{}) (int, error) {
	return io.WriteString(w, Sprintln(vals...))
}

// Print writes the representation of vals to standard output.
func Print(vals ...interface{}) (int, error) {
	return Fprint(os.Stdout, vals...)
}

// Println writes the representation of vals to standard output followed by a
// newline.
func Println(vals ...interface{}) (int, error) {
	return Fprintln(os.Stdout, vals...)
}

func (p *printer) write(v reflect.Value, indent int) {
	if !v.IsValid() {
		p.sb.WriteString("nil")
		return
	}

	switch v.Kind() {
	case reflect.Bool:
		p.sb.WriteString(strconv.FormatBool(v.Bool()))
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		p.sb.WriteString(strconv.FormatInt(v.Int(), 10))
	case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64, reflect.Uintptr:
		p.sb.WriteString(strconv.FormatUint(v.Uint(), 10))
	case reflect.Float32, reflect.Float64:
		p.sb.WriteString(strconv.FormatFloat(v.Float(), 'g', -1, v.Type().Bits()))
	case reflect.Complex64, reflect.Complex128:
		fmt.Fprintf(&p.sb, "%v", v.Complex())
	case reflect.String:
		p.sb.WriteString(strconv.Quote(v.String()))
	case reflect.Interface:
		if v.IsNil() {
			p.sb.WriteString("nil")
			return
		}
		p.write(v.Elem(), indent)
	case reflect.Ptr:
		p.writePtr(v, indent)
	case reflect.Struct:
		p.writeStruct(v, indent)
	case reflect.Slice, reflect.Array:
		p.writeSlice(v, indent)
	case reflect.Map:
		p.writeMap(v, indent)
	case reflect.Chan, reflect.Func:
		p.writeRef(v)
	case reflect.UnsafePointer:
		p.sb.WriteString(v.Type().String())
		p.sb.WriteByte('(')
		p.sb.WriteString(strconv.FormatUint(uint64(v.Pointer()), 16))
		p.sb.WriteByte(')')
	default:
		p.fallback(v)
	}
}

func (p *printer) writePtr(v reflect.Value, indent int) {
	if v.IsNil() {
		p.sb.WriteByte('(')
		p.sb.WriteString(v.Type().String())
		p.sb.WriteString(")(nil)")
		return
	}

	key := visit{v.Type(), v.Pointer()}
	if p.seen[key] {
		p.writeCycle(v.Type())
		return
	}
	p.seen[key] = true
	defer delete(p.seen, key)

	p.sb.WriteByte('&')
	p.write(v.Elem(), indent)
}

func (p *printer) writeStruct(v reflect.Value, indent int) {
	t := v.Type()
	if name := t.Name(); name != "" {
		p.sb.WriteString(name)
	}
	p.sb.WriteByte('{')

	n := t.NumField()
	for i := 0; i < n; i++ {
		p.newline(indent + 1)
		p.sb.WriteString(t.Field(i).Name)
		p.sb.WriteString(": ")
		p.write(v.Field(i), indent+1)
		p.sb.WriteByte(',')
	}
	if n > 0 {
		p.newline(indent)
	}
	p.sb.WriteByte('}')
}

func (p *printer) writeSlice(v reflect.Value, indent int) {
	t := v.Type()
	if v.Kind() == reflect.Slice && v.IsNil() {
		p.sb.WriteString(t.String())
		p.sb.WriteString("(nil)")
		return
	}

	if v.Kind() == reflect.Slice && v.Len() > 0 {
		key := visit{t, v.Pointer()}
		if p.seen[key] {
			p.writeCycle(t)
			return
		}
		p.seen[key] = true
		defer delete(p.seen, key)
	}

	p.sb.WriteString(t.String())
	p.sb.WriteByte('{')
	for i := 0; i < v.Len(); i++ {
		p.newline(indent + 1)
		p.write(v.Index(i), indent+1)
		p.sb.WriteByte(',')
	}
	if v.Len() > 0 {
		p.newline(indent)
	}
	p.sb.WriteByte('}')
}

func (p *printer) writeMap(v reflect.Value, indent int) {
	t := v.Type()
	if v.IsNil() {
		p.sb.WriteString(t.String())
		p.sb.WriteString("(nil)")
		return
	}

	key := visit{t, v.Pointer()}
	if p.seen[key] {
		p.writeCycle(t)
		return
	}
	p.seen[key] = true
	defer delete(p.seen, key)

	keys := v.MapKeys()
	sort.Slice(keys, func(i, j int) bool { return keyString(keys[i]) < keyString(keys[j]) })

	p.sb.WriteString(t.String())
	p.sb.WriteByte('{')
	for _, k := range keys {
		p.newline(indent + 1)
		p.write(k, indent+1)
		p.sb.WriteString(": ")
		p.write(v.MapIndex(k), indent+1)
		p.sb.WriteByte(',')
	}
	if len(keys) > 0 {
		p.newline(indent)
	}
	p.sb.WriteByte('}')
}

func (p *printer) writeRef(v reflect.Value) {
	if v.IsNil() {
		p.sb.WriteString(v.Type().String())
		p.sb.WriteString("(nil)")
		return
	}
	p.sb.WriteString(v.Type().String())
	p.sb.WriteByte('(')
	p.sb.WriteString(strconv.FormatUint(uint64(v.Pointer()), 16))
	p.sb.WriteByte(')')
}

func (p *printer) writeCycle(t reflect.Type) {
	p.sb.WriteString("<cycle ")
	p.sb.WriteString(t.String())
	p.sb.WriteByte('>')
}

func (p *printer) fallback(v reflect.Value) {
	if v.CanInterface() {
		fmt.Fprintf(&p.sb, "%#v", v.Interface())
		return
	}
	p.sb.WriteString(v.Type().String())
}

func (p *printer) newline(indent int) {
	p.sb.WriteByte('\n')
	for i := 0; i < indent; i++ {
		p.sb.WriteString(indentUnit)
	}
}

func keyString(v reflect.Value) string {
	if !v.IsValid() {
		return "<nil>"
	}
	if v.CanInterface() {
		return fmt.Sprintf("%#v", v.Interface())
	}
	return v.Type().String()
}
