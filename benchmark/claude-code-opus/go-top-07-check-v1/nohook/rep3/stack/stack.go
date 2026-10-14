// Package stack provides a minimal LIFO stack, used here as an example
// subject for gocheck-style test suites.
package stack

import "errors"

// ErrEmpty is returned when popping from an empty stack.
var ErrEmpty = errors.New("stack: empty")

// Stack is a LIFO collection of ints.
type Stack struct {
	items []int
}

// Push adds v to the top of the stack.
func (s *Stack) Push(v int) { s.items = append(s.items, v) }

// Pop removes and returns the top element.
func (s *Stack) Pop() (int, error) {
	if len(s.items) == 0 {
		return 0, ErrEmpty
	}
	v := s.items[len(s.items)-1]
	s.items = s.items[:len(s.items)-1]
	return v, nil
}

// Len returns the number of elements on the stack.
func (s *Stack) Len() int { return len(s.items) }
