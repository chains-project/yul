// Package godump renders arbitrary Go values as deeply indented,
// human-readable text suitable for debugging.
//
// It walks values with reflection, so it can inspect types that do not
// implement fmt.Stringer, including unexported struct fields. Pointer cycles
// are detected and reported instead of recursing forever.
package godump

import (
	"fmt"
	"reflect"
	"sort"
	"strconv"
	"strings"
)

const (
	defaultMaxDepth = 64
	indentUnit      = "    "
)

// Printer controls how values are rendered. The zero value is ready to use.
type Printer struct {
	// MaxDepth caps recursion into nested values. Zero selects
	// defaultMaxDepth; a negative value disables the limit.
	MaxDepth int

	out     strings.Builder
	depth   int
	visited map[visit]bool
}

type visit struct {
	ptr uintptr
	typ reflect.Type
}

// Sdump returns the pretty-printed form of values.
func Sdump(values ...any) string {
	return (&Printer{}).Sdump(values...)
}

// Dump writes the pretty-printed form of values to standard output.
func Dump(values ...any) {
	fmt.Print(Sdump(values...))
}

// Sdump renders values using the printer's configuration.
func (p *Printer) Sdump(values ...any) string {
	p.out.Reset()
	p.visited = make(map[visit]bool)
	for i, v := range values {
		if i > 0 {
			p.out.WriteByte('\n')
		}
		p.depth = 0
		p.print(reflect.ValueOf(v))
	}
	return p.out.String()
}

func (p *Printer) depthLimit() int {
	if p.MaxDepth == 0 {
		return defaultMaxDepth
	}
	return p.MaxDepth
}

func (p *Printer) print(v reflect.Value) {
	if !v.IsValid() {
		p.out.WriteString("<invalid>")
		return
	}
	if max := p.depthLimit(); max > 0 && p.depth > max {
		p.out.WriteString("...")
		return
	}

	switch v.Kind() {
	case reflect.Bool:
		p.out.WriteString(strconv.FormatBool(v.Bool()))
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		p.out.WriteString(strconv.FormatInt(v.Int(), 10))
	case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64:
		p.out.WriteString(strconv.FormatUint(v.Uint(), 10))
	case reflect.Uintptr:
		p.out.WriteString("0x" + strconv.FormatUint(v.Uint(), 16))
	case reflect.Float32, reflect.Float64:
		p.out.WriteString(strconv.FormatFloat(v.Float(), 'g', -1, v.Type().Bits()))
	case reflect.Complex64, reflect.Complex128:
		p.out.WriteString(strconv.FormatComplex(v.Complex(), 'g', -1, v.Type().Bits()))
	case reflect.String:
		p.out.WriteString(strconv.Quote(v.String()))
	case reflect.Interface:
		p.printInterface(v)
	case reflect.Pointer:
		p.printPointer(v)
	case reflect.Struct:
		p.printStruct(v)
	case reflect.Array:
		p.printArray(v)
	case reflect.Slice:
		p.printSlice(v)
	case reflect.Map:
		p.printMap(v)
	case reflect.Chan:
		if v.IsNil() {
			p.writeNil(v)
			return
		}
		fmt.Fprintf(&p.out, "(%s)(0x%x)", v.Type(), v.Pointer())
	case reflect.Func:
		if v.IsNil() {
			p.writeNil(v)
			return
		}
		fmt.Fprintf(&p.out, "(%s)(0x%x)", v.Type(), v.Pointer())
	case reflect.UnsafePointer:
		if v.IsNil() {
			p.writeNil(v)
			return
		}
		fmt.Fprintf(&p.out, "unsafe.Pointer(0x%x)", v.Pointer())
	default:
		fmt.Fprintf(&p.out, "<%s>", v.Kind())
	}
}

func (p *Printer) printInterface(v reflect.Value) {
	if v.IsNil() {
		p.out.WriteString("nil")
		return
	}
	elem := v.Elem()
	switch elem.Kind() {
	case reflect.Struct, reflect.Map, reflect.Slice, reflect.Array, reflect.Pointer:
		// These forms already carry their type name.
		p.print(elem)
	default:
		// Keep the dynamic type visible for otherwise ambiguous scalars.
		p.out.WriteString(elem.Type().String())
		p.out.WriteByte('(')
		p.print(elem)
		p.out.WriteByte(')')
	}
}

func (p *Printer) printPointer(v reflect.Value) {
	if v.IsNil() {
		p.writeNil(v)
		return
	}
	if p.enter(v) {
		fmt.Fprintf(&p.out, "<cycle: %s>", v.Type())
		return
	}
	p.out.WriteByte('&')
	p.print(v.Elem())
	p.exit(v)
}

func (p *Printer) printStruct(v reflect.Value) {
	t := v.Type()
	p.out.WriteString(t.String())
	if t.NumField() == 0 {
		p.out.WriteString("{}")
		return
	}
	p.out.WriteString("{\n")
	p.depth++
	for i := 0; i < t.NumField(); i++ {
		field := t.Field(i)
		p.writeIndent()
		p.out.WriteString(field.Name)
		p.out.WriteString(": ")
		p.print(v.Field(i))
		p.out.WriteString(",\n")
	}
	p.depth--
	p.writeIndent()
	p.out.WriteByte('}')
}

func (p *Printer) printArray(v reflect.Value) {
	p.out.WriteString(v.Type().String())
	p.printSequence(v)
}

func (p *Printer) printSlice(v reflect.Value) {
	if v.IsNil() {
		p.writeNil(v)
		return
	}
	if p.enter(v) {
		fmt.Fprintf(&p.out, "<cycle: %s>", v.Type())
		return
	}
	defer p.exit(v)
	p.out.WriteString(v.Type().String())
	p.printSequence(v)
}

func (p *Printer) printSequence(v reflect.Value) {
	if v.Len() == 0 {
		p.out.WriteString("{}")
		return
	}
	if p.multiline(v.Type().Elem()) {
		p.out.WriteString("{\n")
		p.depth++
		for i := 0; i < v.Len(); i++ {
			p.writeIndent()
			p.print(v.Index(i))
			p.out.WriteString(",\n")
		}
		p.depth--
		p.writeIndent()
		p.out.WriteByte('}')
		return
	}
	p.out.WriteByte('{')
	for i := 0; i < v.Len(); i++ {
		if i > 0 {
			p.out.WriteString(", ")
		}
		p.print(v.Index(i))
	}
	p.out.WriteByte('}')
}

func (p *Printer) printMap(v reflect.Value) {
	if v.IsNil() {
		p.writeNil(v)
		return
	}
	if p.enter(v) {
		fmt.Fprintf(&p.out, "<cycle: %s>", v.Type())
		return
	}
	defer p.exit(v)
	p.out.WriteString(v.Type().String())

	keys := v.MapKeys()
	if len(keys) == 0 {
		p.out.WriteString("{}")
		return
	}
	sort.Slice(keys, func(i, j int) bool {
		return formatValue(keys[i]) < formatValue(keys[j])
	})

	if len(keys) > 4 || p.multiline(v.Type().Elem()) {
		p.out.WriteString("{\n")
		p.depth++
		for _, k := range keys {
			p.writeIndent()
			p.print(k)
			p.out.WriteString(": ")
			p.print(v.MapIndex(k))
			p.out.WriteString(",\n")
		}
		p.depth--
		p.writeIndent()
		p.out.WriteByte('}')
		return
	}
	p.out.WriteByte('{')
	for i, k := range keys {
		if i > 0 {
			p.out.WriteString(", ")
		}
		p.print(k)
		p.out.WriteString(": ")
		p.print(v.MapIndex(k))
	}
	p.out.WriteByte('}')
}

// multiline reports whether values of type t read better one-per-line.
func (p *Printer) multiline(t reflect.Type) bool {
	switch t.Kind() {
	case reflect.Struct, reflect.Map, reflect.Slice, reflect.Array, reflect.Pointer:
		return true
	}
	return false
}

func (p *Printer) writeNil(v reflect.Value) {
	p.out.WriteString(v.Type().String())
	p.out.WriteString("(nil)")
}

func (p *Printer) writeIndent() {
	for i := 0; i < p.depth; i++ {
		p.out.WriteString(indentUnit)
	}
}

// enter records v on the active traversal path and reports whether it was
// already present, which indicates a reference cycle.
func (p *Printer) enter(v reflect.Value) bool {
	if p.visited == nil {
		p.visited = make(map[visit]bool)
	}
	key := visit{ptr: v.Pointer(), typ: v.Type()}
	if p.visited[key] {
		return true
	}
	p.visited[key] = true
	return false
}

func (p *Printer) exit(v reflect.Value) {
	delete(p.visited, visit{ptr: v.Pointer(), typ: v.Type()})
}

// formatValue renders v with a throwaway printer, used to derive a stable
// sort key for map entries without going through any.
func formatValue(v reflect.Value) string {
	sub := &Printer{visited: make(map[visit]bool)}
	sub.print(v)
	return sub.out.String()
}
