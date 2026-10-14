// Package calc is a placeholder package demonstrating the test setup.
package calc

// Accumulator keeps a running total.
type Accumulator struct {
	total int
}

// Add adds n to the running total and returns the new total.
func (a *Accumulator) Add(n int) int {
	a.total += n
	return a.total
}

// Total returns the current running total.
func (a *Accumulator) Total() int {
	return a.total
}

// Reset sets the running total back to zero.
func (a *Accumulator) Reset() {
	a.total = 0
}
