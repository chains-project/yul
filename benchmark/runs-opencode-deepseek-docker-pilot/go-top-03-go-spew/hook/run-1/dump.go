package debugprint

import (
	"bytes"
	"fmt"
	"io"
	"os"
	"reflect"
	"sort"
	"strconv"
	"unsafe"
)

type Config struct {
	Indent                  string
	MaxDepth                int
	DisableMethods          bool
	DisablePointerAddresses bool
	DisableCapacities       bool
	SortKeys                bool
}

var DefaultConfig = Config{Indent: " "}

func Dump(a ...any) {
	Fdump(os.Stdout, a...)
}

func Sdump(a ...any) string {
	var buf bytes.Buffer
	Fdump(&buf, a...)
	return buf.String()
}

func Fdump(w io.Writer, a ...any) error {
	return fdump(w, DefaultConfig, a...)
}

func fdump(w io.Writer, cfg Config, a ...any) error {
	ew := &errWriter{w: w}
	d := &dumper{cfg: cfg, writer: ew, ptrs: map[uintptr]bool{}}
	for _, v := range a {
		d.depth = 0
		if v == nil {
			ew.writeString("<nil>\n")
			continue
		}
		d.dump(reflect.ValueOf(v))
		ew.writeString("\n")
	}
	return ew.err
}

type errWriter struct {
	w   io.Writer
	err error
}

func (e *errWriter) Write(p []byte) (int, error) {
	if e.err != nil {
		return 0, e.err
	}
	n, err := e.w.Write(p)
	if err != nil {
		e.err = err
	}
	return n, err
}

func (e *errWriter) writeString(s string) {
	if e.err == nil {
		_, e.err = io.WriteString(e.w, s)
	}
}

type dumper struct {
	cfg    Config
	writer *errWriter
	ptrs   map[uintptr]bool
	depth  int
}

func (d *dumper) dump(v reflect.Value) {
	d.dumpWithType(v, true)
}

func (d *dumper) dumpWithType(v reflect.Value, showType bool) {
	if !v.IsValid() {
		d.writer.writeString("<invalid>")
		return
	}
	if d.cfg.MaxDepth > 0 && d.depth >= d.cfg.MaxDepth {
		d.header(v)
		d.writer.writeString("...")
		return
	}
	if s, ok := d.methodValue(v); ok {
		d.header(v)
		d.writer.writeString(" ")
		d.writer.writeString(strconv.Quote(s))
		return
	}
	switch v.Kind() {
	case reflect.Bool:
		d.prefix(v, showType)
		d.writer.writeString(strconv.FormatBool(v.Bool()))
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		d.prefix(v, showType)
		d.writer.writeString(strconv.FormatInt(v.Int(), 10))
	case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64, reflect.Uintptr:
		d.prefix(v, showType)
		d.writer.writeString(strconv.FormatUint(v.Uint(), 10))
	case reflect.Float32, reflect.Float64:
		d.prefix(v, showType)
		d.writer.writeString(strconv.FormatFloat(v.Float(), 'g', -1, v.Type().Bits()))
	case reflect.Complex64, reflect.Complex128:
		d.prefix(v, showType)
		bits := v.Type().Bits() / 2
		c := v.Complex()
		d.writer.writeString("(" + strconv.FormatFloat(real(c), 'g', -1, bits) + "+" +
			strconv.FormatFloat(imag(c), 'g', -1, bits) + "i)")
	case reflect.String:
		d.prefix(v, showType)
		d.writer.writeString("(len=" + strconv.Itoa(v.Len()) + ") " + strconv.Quote(v.String()))
	case reflect.Ptr, reflect.UnsafePointer:
		d.dumpPtr(v, showType)
	case reflect.Interface:
		d.dumpInterface(v, showType)
	case reflect.Struct:
		d.dumpStruct(v, showType)
	case reflect.Slice:
		d.dumpSlice(v, showType)
	case reflect.Array:
		d.dumpArray(v, showType)
	case reflect.Map:
		d.dumpMap(v, showType)
	case reflect.Chan:
		d.dumpChan(v, showType)
	case reflect.Func:
		d.dumpFunc(v, showType)
	default:
		d.prefix(v, showType)
		rv := readable(v)
		if rv.CanInterface() {
			fmt.Fprintf(d.writer, "%v", rv.Interface())
		}
	}
}

func (d *dumper) prefix(v reflect.Value, showType bool) {
	if showType {
		d.header(v)
		d.writer.writeString(" ")
	}
}

func (d *dumper) header(v reflect.Value) {
	d.writer.writeString("(")
	d.writer.writeString(v.Type().String())
	d.writer.writeString(")")
}

func (d *dumper) dumpPtr(v reflect.Value, showType bool) {
	if v.IsNil() {
		if showType {
			d.header(v)
		}
		d.writer.writeString(" nil")
		return
	}
	addr := v.Pointer()
	if d.ptrs[addr] {
		if showType {
			d.header(v)
		}
		d.writer.writeString(" <already shown>")
		if !d.cfg.DisablePointerAddresses {
			fmt.Fprintf(d.writer, " (0x%x)", addr)
		}
		return
	}
	d.ptrs[addr] = true
	defer delete(d.ptrs, addr)
	if showType {
		d.header(v)
	}
	if !d.cfg.DisablePointerAddresses {
		fmt.Fprintf(d.writer, "(0x%x)", addr)
	}
	d.writer.writeString(" ")
	d.depth++
	d.dumpWithType(v.Elem(), false)
	d.depth--
}

func (d *dumper) dumpInterface(v reflect.Value, showType bool) {
	if v.IsNil() {
		if showType {
			d.header(v)
		}
		d.writer.writeString(" nil")
		return
	}
	if showType {
		d.header(v)
	}
	d.dumpWithType(v.Elem(), true)
}

func (d *dumper) dumpStruct(v reflect.Value, showType bool) {
	if showType {
		d.header(v)
	}
	if !v.CanAddr() {
		n := reflect.New(v.Type()).Elem()
		n.Set(v)
		v = n
	}
	d.writer.writeString("{")
	n := v.NumField()
	for i := 0; i < n; i++ {
		d.writer.writeString("\n")
		d.depth++
		d.indent()
		d.writer.writeString(v.Type().Field(i).Name)
		d.writer.writeString(": ")
		d.dumpWithType(readable(v.Field(i)), true)
		d.depth--
	}
	if n > 0 {
		d.writer.writeString("\n")
		d.indent()
	}
	d.writer.writeString("}")
}

func (d *dumper) dumpSlice(v reflect.Value, showType bool) {
	if v.IsNil() {
		if showType {
			d.header(v)
		}
		d.writer.writeString(" nil")
		return
	}
	addr := v.Pointer()
	if addr != 0 && d.ptrs[addr] {
		if showType {
			d.header(v)
		}
		d.writer.writeString(" <already shown>")
		if !d.cfg.DisablePointerAddresses {
			fmt.Fprintf(d.writer, " (0x%x)", addr)
		}
		return
	}
	if addr != 0 {
		d.ptrs[addr] = true
		defer delete(d.ptrs, addr)
	}
	if showType {
		d.header(v)
	}
	if !d.cfg.DisableCapacities {
		fmt.Fprintf(d.writer, "[%d/%d]", v.Len(), v.Cap())
	} else {
		fmt.Fprintf(d.writer, "[%d]", v.Len())
	}
	d.dumpElements(v)
}

func (d *dumper) dumpArray(v reflect.Value, showType bool) {
	if showType {
		d.header(v)
	}
	fmt.Fprintf(d.writer, "[%d]", v.Len())
	d.dumpElements(v)
}

func (d *dumper) dumpElements(v reflect.Value) {
	d.writer.writeString("{")
	n := v.Len()
	for i := 0; i < n; i++ {
		d.writer.writeString("\n")
		d.depth++
		d.indent()
		d.dump(v.Index(i))
		d.depth--
	}
	if n > 0 {
		d.writer.writeString("\n")
		d.indent()
	}
	d.writer.writeString("}")
}

func (d *dumper) dumpMap(v reflect.Value, showType bool) {
	if v.IsNil() {
		if showType {
			d.header(v)
		}
		d.writer.writeString(" nil")
		return
	}
	addr := v.Pointer()
	if d.ptrs[addr] {
		if showType {
			d.header(v)
		}
		d.writer.writeString(" <already shown>")
		if !d.cfg.DisablePointerAddresses {
			fmt.Fprintf(d.writer, " (0x%x)", addr)
		}
		return
	}
	d.ptrs[addr] = true
	defer delete(d.ptrs, addr)
	if showType {
		d.header(v)
	}
	fmt.Fprintf(d.writer, "(len=%d)", v.Len())
	d.writer.writeString("{")
	keys := v.MapKeys()
	if d.cfg.SortKeys {
		d.sortKeys(keys)
	}
	for _, k := range keys {
		d.writer.writeString("\n")
		d.depth++
		d.indent()
		d.dump(k)
		d.writer.writeString(": ")
		d.dump(v.MapIndex(k))
		d.depth--
	}
	if len(keys) > 0 {
		d.writer.writeString("\n")
		d.indent()
	}
	d.writer.writeString("}")
}

func (d *dumper) dumpChan(v reflect.Value, showType bool) {
	if showType {
		d.header(v)
	}
	if v.IsNil() {
		d.writer.writeString(" nil")
		return
	}
	if !d.cfg.DisableCapacities {
		fmt.Fprintf(d.writer, "[%d/%d]", v.Len(), v.Cap())
	}
	if !d.cfg.DisablePointerAddresses {
		fmt.Fprintf(d.writer, "(0x%x)", v.Pointer())
	}
}

func (d *dumper) dumpFunc(v reflect.Value, showType bool) {
	if showType {
		d.header(v)
	}
	if v.IsNil() {
		d.writer.writeString(" nil")
		return
	}
	if !d.cfg.DisablePointerAddresses {
		fmt.Fprintf(d.writer, "(0x%x)", v.Pointer())
	}
}

func (d *dumper) indent() {
	if d.cfg.Indent == "" {
		return
	}
	for i := 0; i < d.depth; i++ {
		d.writer.writeString(d.cfg.Indent)
	}
}

func (d *dumper) methodValue(v reflect.Value) (string, bool) {
	if d.cfg.DisableMethods {
		return "", false
	}
	switch v.Kind() {
	case reflect.Chan, reflect.Func, reflect.Interface, reflect.Map, reflect.Ptr, reflect.Slice, reflect.UnsafePointer:
		if v.IsNil() {
			return "", false
		}
	}
	if !v.CanInterface() {
		return "", false
	}
	if s, ok := v.Interface().(fmt.Stringer); ok {
		return safeString(s.String), true
	}
	if e, ok := v.Interface().(error); ok {
		return safeString(e.Error), true
	}
	return "", false
}

func (d *dumper) sortKeys(keys []reflect.Value) {
	if len(keys) < 2 {
		return
	}
	switch keys[0].Kind() {
	case reflect.String:
		sort.Slice(keys, func(i, j int) bool { return keys[i].String() < keys[j].String() })
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		sort.Slice(keys, func(i, j int) bool { return keys[i].Int() < keys[j].Int() })
	case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64, reflect.Uintptr:
		sort.Slice(keys, func(i, j int) bool { return keys[i].Uint() < keys[j].Uint() })
	case reflect.Float32, reflect.Float64:
		sort.Slice(keys, func(i, j int) bool { return keys[i].Float() < keys[j].Float() })
	}
}

func readable(v reflect.Value) reflect.Value {
	if v.CanInterface() {
		return v
	}
	if v.CanAddr() {
		return reflect.NewAt(v.Type(), unsafe.Pointer(v.UnsafeAddr())).Elem()
	}
	return v
}

func safeString(f func() string) (s string) {
	defer func() {
		if recover() != nil {
			s = "<panic>"
		}
	}()
	return f()
}
