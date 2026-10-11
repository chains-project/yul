// Package mapx provides a fluent, chainable API for reading and writing
// arbitrary map[string]interface{} data.
//
// A Wrapper is created with New and exposes chainable setters:
//
//	data := mapx.New(nil).
//		Set("user.name", "Ada").
//		Set("user.age", 36).
//		Set("user.tags[0]", "admin").
//		Data()
//
// Reads navigate dotted paths with optional slice indices and are collected
// through a Value that carries any conversion or lookup error:
//
//	name := mapx.New(data).Get("user.name").String()
//	age := mapx.New(data).Get("user.age").Int()
package mapx

import (
	"errors"
	"fmt"
	"sort"
)

// Errors reported by the package. Use errors.Is to test them.
var (
	ErrNotFound     = errors.New("mapx: not found")
	ErrTypeMismatch = errors.New("mapx: type mismatch")
	ErrInvalidPath  = errors.New("mapx: invalid path")
)

// Map is the data shape operated on by the package.
type Map map[string]interface{}

// Wrapper carries a map and the first error encountered while chaining.
// Methods never panic; call Err to inspect the accumulated error.
type Wrapper struct {
	m   Map
	err error
}

// New returns a Wrapper over m. A nil map is replaced with an empty one.
func New(m map[string]interface{}) *Wrapper {
	if m == nil {
		m = map[string]interface{}{}
	}
	return &Wrapper{m: Map(m)}
}

// From is an alias for New.
func From(m map[string]interface{}) *Wrapper { return New(m) }

// Data returns the underlying map.
func (w *Wrapper) Data() map[string]interface{} { return map[string]interface{}(w.m) }

// Err returns the first error encountered while chaining, if any.
func (w *Wrapper) Err() error { return w.err }

// Get resolves path and returns a Value. Missing keys or bad conversions set
// the error on the returned Value rather than panicking.
func (w *Wrapper) Get(path string) *Value {
	if w.err != nil {
		return &Value{err: w.err}
	}
	v, err := lookup(w.m, path)
	return &Value{raw: v, err: err}
}

// Set assigns value at path, creating intermediate maps (and slices when the
// next path segment is an index) as needed. It returns the Wrapper for chaining.
func (w *Wrapper) Set(path string, value interface{}) *Wrapper {
	if w.err != nil {
		return w
	}
	if err := assign(w.m, path, value); err != nil {
		w.err = err
	}
	return w
}

// Merge copies every top-level key of other into the wrapped map.
func (w *Wrapper) Merge(other map[string]interface{}) *Wrapper {
	if w.err != nil {
		return w
	}
	for k, v := range other {
		w.m[k] = v
	}
	return w
}

// Delete removes the value at path. Removing a slice element sets it to nil.
func (w *Wrapper) Delete(path string) *Wrapper {
	if w.err != nil {
		return w
	}
	if err := remove(w.m, path); err != nil {
		w.err = err
	}
	return w
}

// Has reports whether path resolves to a value.
func (w *Wrapper) Has(path string) bool {
	if w.err != nil {
		return false
	}
	_, err := lookup(w.m, path)
	return err == nil
}

// Len returns the number of top-level keys.
func (w *Wrapper) Len() int { return len(w.m) }

// Keys returns the top-level keys in sorted order.
func (w *Wrapper) Keys() []string {
	keys := make([]string, 0, len(w.m))
	for k := range w.m {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	return keys
}

// Clone returns a Wrapper over a deep copy of the wrapped map.
func (w *Wrapper) Clone() *Wrapper {
	return &Wrapper{m: Map(deepCopyMap(w.m))}
}

// String implements fmt.Stringer.
func (w *Wrapper) String() string { return fmt.Sprintf("%v", w.m) }

func deepCopy(v interface{}) interface{} {
	switch t := v.(type) {
	case map[string]interface{}:
		return deepCopyMap(t)
	case Map:
		return Map(deepCopyMap(t))
	case []interface{}:
		out := make([]interface{}, len(t))
		for i, e := range t {
			out[i] = deepCopy(e)
		}
		return out
	default:
		return v
	}
}

func deepCopyMap(m map[string]interface{}) map[string]interface{} {
	out := make(map[string]interface{}, len(m))
	for k, v := range m {
		out[k] = deepCopy(v)
	}
	return out
}
