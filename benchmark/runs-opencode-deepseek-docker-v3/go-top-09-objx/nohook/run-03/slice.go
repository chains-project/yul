package chainmap

import "fmt"

// Slice is a fluent wrapper around a []interface{}. Like Map and Value it
// records the first error encountered and exposes it through Err.
type Slice struct {
	data []interface{}
	err  error
}

// NewSlice returns a Slice wrapping data. A nil slice is replaced with an
// empty slice. The slice is used directly, not copied.
func NewSlice(data []interface{}) *Slice {
	if data == nil {
		data = make([]interface{}, 0)
	}
	return &Slice{data: data}
}

// Raw returns the underlying slice. Mutating it mutates the Slice.
func (s *Slice) Raw() []interface{} {
	if s == nil {
		return nil
	}
	return s.data
}

// Err returns the first error recorded during the chain, if any.
func (s *Slice) Err() error {
	if s == nil {
		return nil
	}
	return s.err
}

// Len returns the number of elements.
func (s *Slice) Len() int {
	if s == nil || s.data == nil {
		return 0
	}
	return len(s.data)
}

// Index returns the element at i, recording ErrIndexOutOfRange when i is
// invalid.
func (s *Slice) Index(i int) *Value {
	if s == nil {
		return errValue(fmt.Errorf("%w: %d", ErrIndexOutOfRange, i))
	}
	if s.err != nil {
		return errValue(s.err)
	}
	if i < 0 || i >= len(s.data) {
		return errValue(fmt.Errorf("%w: %d", ErrIndexOutOfRange, i))
	}
	return newValue(s.data[i])
}

// Values returns every element as a *Value.
func (s *Slice) Values() []*Value {
	if s == nil || s.data == nil {
		return nil
	}
	out := make([]*Value, 0, len(s.data))
	for _, v := range s.data {
		out = append(out, newValue(v))
	}
	return out
}

// Each calls fn for every element in order. Returning false stops the
// iteration early. It returns the receiver for chaining.
func (s *Slice) Each(fn func(i int, v *Value) bool) *Slice {
	if s == nil || s.err != nil {
		return s
	}
	for i, v := range s.data {
		if !fn(i, newValue(v)) {
			break
		}
	}
	return s
}

// Append adds values to the end of the slice and returns the receiver for
// chaining. Passing a *Map, *Slice, or *Value appends its underlying data.
func (s *Slice) Append(values ...interface{}) *Slice {
	if s == nil || s.err != nil {
		return s
	}
	for _, v := range values {
		s.data = append(s.data, unwrap(v))
	}
	return s
}

// Prepend inserts values at the front of the slice, preserving their order,
// and returns the receiver for chaining.
func (s *Slice) Prepend(values ...interface{}) *Slice {
	if s == nil || s.err != nil || len(values) == 0 {
		return s
	}
	prefix := make([]interface{}, 0, len(values)+len(s.data))
	for _, v := range values {
		prefix = append(prefix, unwrap(v))
	}
	s.data = append(prefix, s.data...)
	return s
}

// Transform replaces every element with the result of fn, returning the
// receiver for chaining.
func (s *Slice) Transform(fn func(i int, v *Value) interface{}) *Slice {
	if s == nil || s.err != nil {
		return s
	}
	for i, v := range s.data {
		s.data[i] = unwrap(fn(i, newValue(v)))
	}
	return s
}

// Filter returns a new Slice containing only the elements for which fn
// reports true. The receiver is left unchanged.
func (s *Slice) Filter(fn func(i int, v *Value) bool) *Slice {
	out := NewSlice(nil)
	if s == nil || s.err != nil {
		return out
	}
	for i, v := range s.data {
		if fn(i, newValue(v)) {
			out.data = append(out.data, v)
		}
	}
	return out
}
