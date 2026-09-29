package deepprint

import (
	"bytes"
	"math"
	"reflect"
	"sort"
	"strconv"
	"strings"
	"unicode/utf8"
)

// visit identifies a reference value by its type and address, used for cycle
// detection while walking the object graph.
type visit struct {
	typ reflect.Type
	ptr uintptr
}

func (p *Printer) formatValue(v reflect.Value) string {
	var b bytes.Buffer
	p.writeValue(&b, v, 0, make(map[visit]bool))
	return b.String()
}

func (p *Printer) writeIndent(b *bytes.Buffer, depth int) {
	for i := 0; i < depth; i++ {
		b.WriteString(p.cfg.Indent)
	}
}

// writePrefix emits the value's type when ShowTypes is enabled.
func (p *Printer) writePrefix(b *bytes.Buffer, v reflect.Value) {
	if !p.cfg.ShowTypes {
		return
	}
	b.WriteByte('(')
	b.WriteString(v.Type().String())
	b.WriteString(") ")
}

func (p *Printer) writeValue(b *bytes.Buffer, v reflect.Value, depth int, seen map[visit]bool) {
	if !v.IsValid() {
		b.WriteString("<nil>")
		return
	}
	if p.cfg.MaxDepth > 0 && depth >= p.cfg.MaxDepth {
		b.WriteString("...")
		return
	}

	switch v.Kind() {
	case reflect.Bool:
		p.writePrefix(b, v)
		b.WriteString(strconv.FormatBool(v.Bool()))

	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		p.writePrefix(b, v)
		b.WriteString(strconv.FormatInt(v.Int(), 10))

	case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64:
		p.writePrefix(b, v)
		b.WriteString(strconv.FormatUint(v.Uint(), 10))

	case reflect.Uintptr:
		p.writePrefix(b, v)
		b.WriteString("0x")
		b.WriteString(strconv.FormatUint(v.Uint(), 16))

	case reflect.Float32, reflect.Float64:
		p.writePrefix(b, v)
		b.WriteString(formatFloat(v.Float(), v.Type().Bits()))

	case reflect.Complex64, reflect.Complex128:
		bits := v.Type().Bits() / 2
		c := v.Complex()
		p.writePrefix(b, v)
		b.WriteByte('(')
		b.WriteString(formatFloat(real(c), bits))
		b.WriteByte('+')
		b.WriteString(formatFloat(imag(c), bits))
		b.WriteString("i)")

	case reflect.String:
		p.writePrefix(b, v)
		b.WriteString(strconv.Quote(v.String()))

	case reflect.Ptr:
		p.writePointer(b, v, depth, seen)

	case reflect.Interface:
		if v.IsNil() {
			p.writePrefix(b, v)
			b.WriteString("<nil>")
			return
		}
		p.writeValue(b, v.Elem(), depth+1, seen)

	case reflect.Struct:
		p.writeStruct(b, v, depth, seen)

	case reflect.Map:
		p.writeMap(b, v, depth, seen)

	case reflect.Slice:
		p.writeSlice(b, v, depth, seen)

	case reflect.Array:
		p.writeArray(b, v, depth, seen)

	case reflect.Chan:
		p.writePrefix(b, v)
		if v.IsNil() {
			b.WriteString("<nil>")
			return
		}
		b.WriteString("0x")
		b.WriteString(strconv.FormatUint(uint64(v.Pointer()), 16))
		b.WriteString(" (len=")
		b.WriteString(strconv.Itoa(v.Len()))
		b.WriteString(" cap=")
		b.WriteString(strconv.Itoa(v.Cap()))
		b.WriteByte(')')

	case reflect.Func:
		p.writePrefix(b, v)
		if v.IsNil() {
			b.WriteString("<nil>")
			return
		}
		b.WriteString("<func>")

	case reflect.UnsafePointer:
		p.writePrefix(b, v)
		if v.Pointer() == 0 {
			b.WriteString("<nil>")
			return
		}
		b.WriteString("0x")
		b.WriteString(strconv.FormatUint(uint64(v.Pointer()), 16))

	default:
		b.WriteString("<unsupported ")
		b.WriteString(v.Kind().String())
		b.WriteByte('>')
	}
}

func (p *Printer) writePointer(b *bytes.Buffer, v reflect.Value, depth int, seen map[visit]bool) {
	if v.IsNil() {
		p.writePrefix(b, v)
		b.WriteString("<nil>")
		return
	}
	key := visit{v.Type(), v.Pointer()}
	if seen[key] {
		p.writePrefix(b, v)
		b.WriteString("<already shown>")
		return
	}
	seen[key] = true
	defer delete(seen, key)

	if p.cfg.ShowPointers {
		b.WriteString("0x")
		b.WriteString(strconv.FormatUint(uint64(v.Pointer()), 16))
		b.WriteByte(' ')
	}
	b.WriteByte('&')
	p.writeValue(b, v.Elem(), depth+1, seen)
}

func (p *Printer) writeStruct(b *bytes.Buffer, v reflect.Value, depth int, seen map[visit]bool) {
	t := v.Type()
	fields := make([]int, 0, v.NumField())
	for i := 0; i < v.NumField(); i++ {
		if !t.Field(i).IsExported() && !p.cfg.ShowUnexported {
			continue
		}
		fields = append(fields, i)
	}

	p.writePrefix(b, v)
	if len(fields) == 0 {
		b.WriteString("{}")
		return
	}
	b.WriteString("{\n")
	for _, i := range fields {
		p.writeIndent(b, depth+1)
		b.WriteString(t.Field(i).Name)
		b.WriteString(": ")
		p.writeValue(b, v.Field(i), depth+1, seen)
		b.WriteString(",\n")
	}
	p.writeIndent(b, depth)
	b.WriteByte('}')
}

func (p *Printer) writeMap(b *bytes.Buffer, v reflect.Value, depth int, seen map[visit]bool) {
	if v.IsNil() {
		p.writePrefix(b, v)
		b.WriteString("<nil>")
		return
	}
	key := visit{v.Type(), v.Pointer()}
	if seen[key] {
		p.writePrefix(b, v)
		b.WriteString("<already shown>")
		return
	}
	seen[key] = true
	defer delete(seen, key)

	p.writePrefix(b, v)
	if v.Len() == 0 {
		b.WriteString("{}")
		return
	}

	type entry struct {
		key string
		val reflect.Value
	}
	entries := make([]entry, 0, v.Len())
	iter := v.MapRange()
	for iter.Next() {
		var kb bytes.Buffer
		p.writeValue(&kb, iter.Key(), depth+1, make(map[visit]bool))
		entries = append(entries, entry{key: kb.String(), val: iter.Value()})
	}
	if p.cfg.SortMapKeys {
		sort.SliceStable(entries, func(i, j int) bool { return entries[i].key < entries[j].key })
	}

	b.WriteString("{\n")
	for _, e := range entries {
		p.writeIndent(b, depth+1)
		b.WriteString(e.key)
		b.WriteString(": ")
		p.writeValue(b, e.val, depth+1, seen)
		b.WriteString(",\n")
	}
	p.writeIndent(b, depth)
	b.WriteByte('}')
}

func (p *Printer) writeSlice(b *bytes.Buffer, v reflect.Value, depth int, seen map[visit]bool) {
	if v.IsNil() {
		p.writePrefix(b, v)
		b.WriteString("<nil>")
		return
	}
	if v.Len() > 0 {
		key := visit{v.Type(), v.Pointer()}
		if seen[key] {
			p.writePrefix(b, v)
			b.WriteString("<already shown>")
			return
		}
		seen[key] = true
		defer delete(seen, key)
	}

	if v.Type().Elem().Kind() == reflect.Uint8 {
		p.writePrefix(b, v)
		b.WriteString(formatBytes(v.Bytes()))
		return
	}

	p.writePrefix(b, v)
	b.WriteString("(len=")
	b.WriteString(strconv.Itoa(v.Len()))
	b.WriteString(" cap=")
	b.WriteString(strconv.Itoa(v.Cap()))
	b.WriteString(") ")
	p.writeIndexed(b, v, depth, seen)
}

func (p *Printer) writeArray(b *bytes.Buffer, v reflect.Value, depth int, seen map[visit]bool) {
	p.writePrefix(b, v)
	p.writeIndexed(b, v, depth, seen)
}

func (p *Printer) writeIndexed(b *bytes.Buffer, v reflect.Value, depth int, seen map[visit]bool) {
	if v.Len() == 0 {
		b.WriteString("{}")
		return
	}
	b.WriteString("{\n")
	for i := 0; i < v.Len(); i++ {
		p.writeIndent(b, depth+1)
		b.WriteString(strconv.Itoa(i))
		b.WriteString(": ")
		p.writeValue(b, v.Index(i), depth+1, seen)
		b.WriteString(",\n")
	}
	p.writeIndent(b, depth)
	b.WriteByte('}')
}

func formatFloat(f float64, bits int) string {
	switch {
	case math.IsNaN(f):
		return "NaN"
	case math.IsInf(f, 1):
		return "+Inf"
	case math.IsInf(f, -1):
		return "-Inf"
	}
	return strconv.FormatFloat(f, 'g', -1, bits)
}

func formatBytes(b []byte) string {
	if len(b) == 0 {
		return "[]byte{}"
	}
	if utf8.Valid(b) {
		return "[]byte(" + strconv.Quote(string(b)) + ")"
	}
	var sb strings.Builder
	sb.WriteString("[]byte{")
	for i, c := range b {
		if i > 0 {
			sb.WriteString(", ")
		}
		sb.WriteString("0x")
		if c < 0x10 {
			sb.WriteByte('0')
		}
		sb.WriteString(strconv.FormatUint(uint64(c), 16))
	}
	sb.WriteByte('}')
	return sb.String()
}
