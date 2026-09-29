package testkit

// Counter is a tiny stateful type used to demonstrate suite-style tests,
// fixtures, and setup/teardown hooks.
type Counter struct {
	value int
}

// Inc increments the counter by one.
func (c *Counter) Inc() { c.value++ }

// Add increments the counter by n.
func (c *Counter) Add(n int) { c.value += n }

// Value reports the current counter value.
func (c *Counter) Value() int { return c.value }

// Reset returns the counter to zero.
func (c *Counter) Reset() { c.value = 0 }
