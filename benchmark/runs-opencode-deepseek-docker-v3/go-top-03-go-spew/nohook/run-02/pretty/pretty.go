package pretty

import (
	"fmt"
	"io"
	"os"
	"reflect"
	"sort"
	"strconv"
	"strings"
)

const (
	maxDepth = 64
	indent   = "  "
)

type visit struct {
	typ reflect.Type
	ptr uintptr
}

type printer struct {
	visited map[visit]bool
}

func Sprint(args ...interface{}) string {
	var b strings.Builder
	for i, arg := range args {
		if i > 0 {
			b.WriteByte(' ')
		}
		p := &printer{visited: make(map[visit]bool)}
		p.value(&b, reflect.ValueOf(arg), 0)
	}
	return b.String()
}

func Print(args ...interface{}) {
	fmt.Print(Sprint(args...))
}

func Println(args ...interface{}) {
	fmt.Println(Sprint(args...))
}

func Fprint(w io.Writer, args ...interface{}) {
	fmt.Fprint(w, Sprint(args...))
}

func Fprintln(w io.Writer, args ...interface{}) {
	fmt.Fprintln(w, Sprint(args...))
}

func Dump(v interface{}) string {
	return Sprint(v)
}

func Fdump(w io.Writer, v interface{}) {
	Fprintln(w, v)
}

func DumpToFile(path string, v interface{}) error {
	f, err := os.Create(path)
	if err != nil {
		return err
	}
	defer f.Close()
	Fprintln(f, v)
	return f.Sync()
}

func (p *printer) value(b *strings.Builder, v reflect.Value, depth int) {
	if !v.IsValid() {
		b.WriteString("<nil>")
		return
	}
	if depth > maxDepth {
		b.WriteString("...")
		return
	}

	switch v.Kind() {
	case reflect.Bool:
		b.WriteString(strconv.FormatBool(v.Bool()))
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		b.WriteString(strconv.FormatInt(v.Int(), 10))
	case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64, reflect.Uintptr:
		b.WriteString(strconv.FormatUint(v.Uint(), 10))
	case reflect.Float32, reflect.Float64:
		b.WriteString(strconv.FormatFloat(v.Float(), 'g', -1, v.Type().Bits()))
	case reflect.Complex64, reflect.Complex128:
		b.WriteString(strconv.FormatComplex(v.Complex(), 'g', -1, v.Type().Bits()))
	case reflect.String:
		b.WriteString(strconv.Quote(v.String()))
	case reflect.Ptr:
		p.pointer(b, v, depth)
	case reflect.Interface:
		if v.IsNil() {
			b.WriteString("<nil>")
			return
		}
		elem := v.Elem()
		b.WriteString(elem.Type().String())
		b.WriteByte('(')
		p.value(b, elem, depth)
		b.WriteByte(')')
	case reflect.Struct:
		p.structValue(b, v, depth)
	case reflect.Map:
		p.mapValue(b, v, depth)
	case reflect.Slice:
		p.sliceValue(b, v, depth)
	case reflect.Array:
		p.arrayValue(b, v, depth)
	case reflect.Chan:
		b.WriteString(v.Type().String())
		b.WriteString("(<")
		b.WriteString(strconv.Itoa(v.Len()))
		b.WriteByte('/')
		b.WriteString(strconv.Itoa(v.Cap()))
		b.WriteString(">)")
	case reflect.Func:
		if v.IsNil() {
			b.WriteString("func<nil>")
			return
		}
		b.WriteString(v.Type().String())
	case reflect.UnsafePointer:
		b.WriteString("unsafe.Pointer(0x")
		b.WriteString(strconv.FormatUint(uint64(v.Pointer()), 16))
		b.WriteByte(')')
	default:
		b.WriteString(v.Type().String())
	}
}

func (p *printer) pointer(b *strings.Builder, v reflect.Value, depth int) {
	if v.IsNil() {
		b.WriteString("(*")
		b.WriteString(v.Type().Elem().String())
		b.WriteString(")(nil)")
		return
	}
	if !p.enter(v) {
		b.WriteString("<cycle>")
		return
	}
	defer p.leave(v)

	b.WriteString("(*")
	b.WriteString(v.Type().Elem().String())
	b.WriteString(")(0x")
	b.WriteString(strconv.FormatUint(uint64(v.Pointer()), 16))
	b.WriteString(" -> ")
	p.value(b, v.Elem(), depth)
	b.WriteByte(')')
}

func (p *printer) structValue(b *strings.Builder, v reflect.Value, depth int) {
	t := v.Type()
	b.WriteString(t.String())
	b.WriteByte('{')
	if v.NumField() == 0 {
		b.WriteByte('}')
		return
	}
	b.WriteByte('\n')
	pad := strings.Repeat(indent, depth+1)
	for i := 0; i < t.NumField(); i++ {
		sf := t.Field(i)
		b.WriteString(pad)
		b.WriteString(sf.Name)
		b.WriteString(": ")
		p.value(b, v.Field(i), depth+1)
		b.WriteByte('\n')
	}
	b.WriteString(strings.Repeat(indent, depth))
	b.WriteByte('}')
}

func (p *printer) mapValue(b *strings.Builder, v reflect.Value, depth int) {
	if v.IsNil() {
		b.WriteString(v.Type().String())
		b.WriteString("(<nil>)")
		return
	}
	if !p.enter(v) {
		b.WriteString("<cycle>")
		return
	}
	defer p.leave(v)

	b.WriteString(v.Type().String())
	b.WriteByte('{')
	keys := v.MapKeys()
	entries := make([]string, 0, len(keys))
	for _, k := range keys {
		var line strings.Builder
		line.WriteString(strings.Repeat(indent, depth+1))
		p.value(&line, k, depth+1)
		line.WriteString(": ")
		p.value(&line, v.MapIndex(k), depth+1)
		entries = append(entries, line.String())
	}
	if len(entries) == 0 {
		b.WriteByte('}')
		return
	}
	sort.Strings(entries)
	b.WriteByte('\n')
	for _, e := range entries {
		b.WriteString(e)
		b.WriteByte('\n')
	}
	b.WriteString(strings.Repeat(indent, depth))
	b.WriteByte('}')
}

func (p *printer) sliceValue(b *strings.Builder, v reflect.Value, depth int) {
	if v.IsNil() {
		b.WriteString(v.Type().String())
		b.WriteString("(<nil>)")
		return
	}
	if !p.enter(v) {
		b.WriteString("<cycle>")
		return
	}
	defer p.leave(v)
	p.elements(b, v, depth)
}

func (p *printer) arrayValue(b *strings.Builder, v reflect.Value, depth int) {
	p.elements(b, v, depth)
}

func (p *printer) elements(b *strings.Builder, v reflect.Value, depth int) {
	b.WriteString(v.Type().String())
	b.WriteByte('{')
	n := v.Len()
	if n == 0 {
		b.WriteByte('}')
		return
	}
	b.WriteByte('\n')
	pad := strings.Repeat(indent, depth+1)
	for i := 0; i < n; i++ {
		b.WriteString(pad)
		p.value(b, v.Index(i), depth+1)
		b.WriteByte('\n')
	}
	b.WriteString(strings.Repeat(indent, depth))
	b.WriteByte('}')
}

func (p *printer) enter(v reflect.Value) bool {
	ptr := v.Pointer()
	if ptr == 0 {
		return true
	}
	key := visit{typ: v.Type(), ptr: ptr}
	if p.visited[key] {
		return false
	}
	p.visited[key] = true
	return true
}

func (p *printer) leave(v reflect.Value) {
	ptr := v.Pointer()
	if ptr == 0 {
		return
	}
	delete(p.visited, visit{typ: v.Type(), ptr: ptr})
}
