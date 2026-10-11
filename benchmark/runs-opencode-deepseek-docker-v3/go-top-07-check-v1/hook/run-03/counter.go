package gosuite

// Counter is a small example type used to demonstrate gocheck test suites.
type Counter struct {
	value int
}

// NewCounter returns a Counter initialized to zero.
func NewCounter() *Counter {
	return &Counter{}
}

// Inc increments the counter by one.
func (c *Counter) Inc() {
	c.value++
}

// Add increments the counter by n.
func (c *Counter) Add(n int) {
	c.value += n
}

// Value returns the current value.
func (c *Counter) Value() int {
	return c.value
}

// Reset sets the counter back to zero.
func (c *Counter) Reset() {
	c.value = 0
}
