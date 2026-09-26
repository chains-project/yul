package gochecktest

// Calc is a simple accumulator used to exercise the test suite's
// fixtures and setup/teardown hooks.
type Calc struct {
	total int
}

func NewCalc() *Calc {
	return &Calc{}
}

func (c *Calc) Add(n int) int {
	c.total += n
	return c.total
}

func (c *Calc) Reset() {
	c.total = 0
}
